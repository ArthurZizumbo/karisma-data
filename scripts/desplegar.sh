#!/usr/bin/env bash
# ===========================================================================
# Karisma Data — Despliegue puente en GCP con base administrada (US-M01)
#
# Uso:
#   bash scripts/desplegar.sh [FASE ...]
#
# Fases admitidas:
#   apis | registro | base | secretos | imagenes | api | migraciones
#   | semillas | web | iam | presupuesto | verificar
#
# Sin argumentos ejecuta todas las fases en orden.
# ===========================================================================
set -euo pipefail

PROYECTO="${PROYECTO:-tareas-computo-nube}"
NUMERO_PROYECTO="${NUMERO_PROYECTO:-$(gcloud projects describe "$PROYECTO" --format='value(projectNumber)' 2>/dev/null || true)}"
CUENTA_FACTURACION="${CUENTA_FACTURACION:-${GCP_BILLING_ACCOUNT:-}}"
REGION="${REGION:-us-central1}"
INSTANCIA="${INSTANCIA:-karisma-pg}"
REPOSITORIO="${REPOSITORIO:-karisma}"
ETIQUETA="${ETIQUETA:-$(git rev-parse --short HEAD)}"
ENV_BACKEND="${ENV_BACKEND:-backend/.env.local}"

# Detección de credenciales ADC
if [ -z "${CREDENCIALES_ADC:-}" ]; then
  if [ -n "${APPDATA:-}" ] && [ -f "${APPDATA}/gcloud/application_default_credentials.json" ]; then
    CREDENCIALES_ADC="${APPDATA}/gcloud/application_default_credentials.json"
  elif [ -f "${HOME}/.config/gcloud/application_default_credentials.json" ]; then
    CREDENCIALES_ADC="${HOME}/.config/gcloud/application_default_credentials.json"
  else
    CREDENCIALES_ADC=""
  fi
fi
export CREDENCIALES_ADC

# Carga de variables locales si existen
if [ -f "$ENV_BACKEND" ]; then
  set -a
  # shellcheck disable=SC1090
  . "$ENV_BACKEND"
  set +a
fi

# Contrasena del usuario de Cloud SQL. Sin valor por omision, y esa ausencia es
# la regla: un fallback escrito aqui viaja al repositorio y de ahi a la base
# administrada, que es exactamente la credencial que nadie deberia poder leer.
# POSTGRES_PASSWORD sirve de origen porque es la que ya vive en .env.local.
KARISMA_DB_PASSWORD="${KARISMA_DB_PASSWORD:-${POSTGRES_PASSWORD:-}}"

log() {
  printf "\n\033[1;34m[US-M01]\033[0m %s\n" "$*"
}

abortar() {
  printf "\n\033[1;31m[US-M01 FALLA]\033[0m %s\n" "$*" >&2
  exit 1
}

# Un secreto que falta detiene el despliegue. Nunca se sustituye por un valor de
# ejemplo: subirlo a Secret Manager lo convierte en el secreto de produccion, y
# el que esta escrito en un repositorio publico no es un secreto.
exigir_secreto() {
  local nombre="$1" valor="$2"
  if [ -z "$valor" ]; then
    abortar "Falta $nombre. Definelo en $ENV_BACKEND o exportalo antes de desplegar; este guion no inventa secretos."
  fi
}

exigir_proyecto() {
  log "Verificando proyecto activo, número y facturación..."
  local proj_actual
  proj_actual=$(gcloud config get-value project 2>/dev/null || true)
  if [ "$proj_actual" != "$PROYECTO" ]; then
    log "Configurando proyecto activo a $PROYECTO..."
    gcloud config set project "$PROYECTO" --quiet
  fi

  # La facturacion se comprueba y se aborta, no se advierte: desplegar contra la
  # cuenta equivocada gasta el presupuesto de otro proyecto y las alertas de
  # CA-9 quedan colgadas de una cuenta que nadie mira.
  local cuenta_act
  cuenta_act=$(gcloud beta billing projects describe "$PROYECTO" --format='value(billingAccountName)' 2>/dev/null || true)
  if [ -z "$CUENTA_FACTURACION" ]; then
    abortar "Falta CUENTA_FACTURACION (o GCP_BILLING_ACCOUNT). Sin ella no se puede comprobar contra que cuenta se gasta."
  fi
  if [ -z "$cuenta_act" ]; then
    abortar "No se pudo leer la cuenta de facturacion de $PROYECTO. Revisa permisos de billing antes de crear un solo recurso."
  fi
  if [ "$cuenta_act" != "billingAccounts/$CUENTA_FACTURACION" ]; then
    abortar "La cuenta de facturacion de $PROYECTO es $cuenta_act y se esperaba billingAccounts/$CUENTA_FACTURACION."
  fi
  log "Proyecto verificado: $PROYECTO ($NUMERO_PROYECTO)"
}

habilitar_apis() {
  log "Habilitando APIs necesarias en GCP..."
  gcloud services enable \
    run.googleapis.com \
    sqladmin.googleapis.com \
    artifactregistry.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    billingbudgets.googleapis.com \
    --project="$PROYECTO" --quiet
  log "APIs habilitadas."
}

crear_registro() {
  log "Configurando repositorio Artifact Registry: $REPOSITORIO..."
  if ! gcloud artifacts repositories describe "$REPOSITORIO" --location="$REGION" --project="$PROYECTO" >/dev/null 2>&1; then
    gcloud artifacts repositories create "$REPOSITORIO" \
      --repository-format=docker \
      --location="$REGION" \
      --description="Imagenes del portal Karisma Data" \
      --project="$PROYECTO" --quiet
  fi

  log "Aplicando política de limpieza de Artifact Registry (3 versiones)..."
  gcloud artifacts repositories set-cleanup-policies "$REPOSITORIO" \
    --location="$REGION" \
    --policy=scripts/limpieza_artifact_registry.json \
    --project="$PROYECTO" --no-dry-run --quiet

  gcloud auth configure-docker "$REGION-docker.pkg.dev" --quiet
  log "Artifact Registry configurado."
}

crear_base() {
  log "Configurando Cloud SQL: $INSTANCIA (PostgreSQL 15 Enterprise db-f1-micro)..."
  if ! gcloud sql instances describe "$INSTANCIA" --project="$PROYECTO" >/dev/null 2>&1; then
    gcloud sql instances create "$INSTANCIA" \
      --database-version=POSTGRES_15 \
      --edition=enterprise \
      --tier=db-f1-micro \
      --region="$REGION" \
      --availability-type=zonal \
      --storage-type=HDD \
      --storage-size=10 \
      --no-storage-auto-increase \
      --no-backup \
      --project="$PROYECTO" --quiet
  fi

  if ! gcloud sql databases describe karisma --instance="$INSTANCIA" --project="$PROYECTO" >/dev/null 2>&1; then
    gcloud sql databases create karisma --instance="$INSTANCIA" --project="$PROYECTO" --quiet
  fi

  if ! gcloud sql users describe karisma --instance="$INSTANCIA" --project="$PROYECTO" >/dev/null 2>&1; then
    gcloud sql users create karisma --instance="$INSTANCIA" --password="$KARISMA_DB_PASSWORD" --project="$PROYECTO" --quiet
  fi
  log "Cloud SQL listo."
}

cargar_secretos() {
  log "Cargando secretos a Secret Manager..."
  exigir_secreto "KARISMA_DB_PASSWORD" "${KARISMA_DB_PASSWORD:-}"
  exigir_secreto "JWT_SECRET_KEY" "${JWT_SECRET_KEY:-}"
  exigir_secreto "GEMINI_API_KEY" "${GEMINI_API_KEY:-}"

  local dsn_prod="postgresql://karisma:${KARISMA_DB_PASSWORD}@/karisma?host=/cloudsql/${PROYECTO}:${REGION}:${INSTANCIA}&sslmode=disable"
  local jwt_key="$JWT_SECRET_KEY"
  local gemini_key="$GEMINI_API_KEY"

  local secret_name
  for secret_name in DATABASE_URL JWT_SECRET_KEY GEMINI_API_KEY; do
    if ! gcloud secrets describe "$secret_name" --project="$PROYECTO" >/dev/null 2>&1; then
      gcloud secrets create "$secret_name" --replication-policy=automatic --project="$PROYECTO" --quiet
    fi
  done

  printf '%s' "$dsn_prod" | gcloud secrets versions add DATABASE_URL --data-file=- --project="$PROYECTO" --quiet
  printf '%s' "$jwt_key" | gcloud secrets versions add JWT_SECRET_KEY --data-file=- --project="$PROYECTO" --quiet
  printf '%s' "$gemini_key" | gcloud secrets versions add GEMINI_API_KEY --data-file=- --project="$PROYECTO" --quiet

  for secret_name in DATABASE_URL JWT_SECRET_KEY GEMINI_API_KEY; do
    gcloud secrets add-iam-policy-binding "$secret_name" \
      --member="serviceAccount:${NUMERO_PROYECTO}-compute@developer.gserviceaccount.com" \
      --role=roles/secretmanager.secretAccessor \
      --project="$PROYECTO" --quiet >/dev/null 2>&1 || true
  done
  log "Secretos sincronizados y permisos concedidos."
}

construir_imagenes() {
  log "Construyendo imágenes con etiqueta $ETIQUETA..."
  local ctx
  ctx=$(mktemp -d 2>/dev/null || mktemp -d -t 'karisma_ctx')

  cp -r backend/* "$ctx/"
  # El glob de arriba no alcanza los archivos ocultos, y uno de ellos decide que
  # entra a la imagen: sin .dockerignore el contexto viaja entero -cache de
  # Python, guias de agentes- y las exclusiones que backend/ declara dejan de
  # aplicarse justo en la construccion que va a produccion.
  cp backend/.dockerignore "$ctx/.dockerignore"
  mkdir -p "$ctx/data"
  if [ -d "data/silos" ]; then
    cp -r data/silos "$ctx/data/"
  fi
  if [ -d "data/aggregates" ]; then
    cp -r data/aggregates "$ctx/data/"
  fi

  log "Construyendo imagen API (target: runtime-con-datos)..."
  docker build --platform linux/amd64 --target runtime-con-datos \
    -t "$REGION-docker.pkg.dev/$PROYECTO/$REPOSITORIO/api:$ETIQUETA" "$ctx"

  rm -rf "$ctx"

  log "Construyendo imagen Web (frontend)..."
  docker build --platform linux/amd64 \
    -t "$REGION-docker.pkg.dev/$PROYECTO/$REPOSITORIO/web:$ETIQUETA" frontend

  log "Subiendo imágenes a Artifact Registry..."
  docker push "$REGION-docker.pkg.dev/$PROYECTO/$REPOSITORIO/api:$ETIQUETA"
  docker push "$REGION-docker.pkg.dev/$PROYECTO/$REPOSITORIO/web:$ETIQUETA"
  log "Imágenes publicadas con éxito."
}

desplegar_api() {
  log "Desplegando servicio karisma-api en Cloud Run (privado)..."
  gcloud run deploy karisma-api \
    --image="$REGION-docker.pkg.dev/$PROYECTO/$REPOSITORIO/api:$ETIQUETA" \
    --region="$REGION" \
    --project="$PROYECTO" \
    --no-allow-unauthenticated \
    --min-instances=0 \
    --max-instances=3 \
    --memory=512Mi \
    --concurrency=80 \
    --add-cloudsql-instances="$PROYECTO:$REGION:$INSTANCIA" \
    --set-secrets=DATABASE_URL=DATABASE_URL:latest,JWT_SECRET_KEY=JWT_SECRET_KEY:latest,GEMINI_API_KEY=GEMINI_API_KEY:latest \
    --set-env-vars=APP_ENV=prod,LOG_LEVEL=INFO,DATA_DIR=/app/data,CHAT_PROVIDER=guionizado,EXPORT_STORAGE_BACKEND=local,DEMO_LOGIN_ENABLED=true \
    --quiet
  # --set-env-vars reemplaza el conjunto entero, asi que una variable que alguien
  # anadio a mano en la consola desaparece en el siguiente despliegue. Es
  # deliberado: el estado del servicio tiene que salir de este guion y de ningun
  # otro sitio, que es lo que significa "sin pasos manuales no escritos".
  log "karisma-api desplegado."
}

aplicar_migraciones() {
  log "Levantando Cloud SQL Auth Proxy vía Compose para aplicar migraciones..."
  exigir_secreto "KARISMA_DB_PASSWORD" "${KARISMA_DB_PASSWORD:-}"
  if [ -z "$CREDENCIALES_ADC" ]; then
    abortar "No se encontraron credenciales de aplicacion. Corre 'gcloud auth application-default login' o define CREDENCIALES_ADC."
  fi
  # Las dos variables que docker-compose.yml exige y deja sin valor por omision.
  export INSTANCIA_CLOUD_SQL="$PROYECTO:$REGION:$INSTANCIA"
  docker compose --profile nube up -d sqlproxy
  sleep 3

  local dbmate_url="postgres://karisma:${KARISMA_DB_PASSWORD}@sqlproxy:5432/karisma?sslmode=disable"
  export DBMATE_URL="$dbmate_url"

  log "Ejecutando dbmate up..."
  bash scripts/dbmate.sh --wait up

  log "Verificando db/schema.sql..."
  git diff --exit-code db/schema.sql || {
    echo "ERROR: db/schema.sql difiere tras dbmate up."
    exit 1
  }
  log "Migraciones aplicadas y db/schema.sql verificado."
}

aplicar_semillas() {
  log "Aplicando semillas de catálogo y linaje..."
  local dbmate_url="postgres://karisma:${KARISMA_DB_PASSWORD}@sqlproxy:5432/karisma?sslmode=disable"
  export DBMATE_URL="$dbmate_url"

  poetry -P backend run python -m ml.data.seed_catalog
  bash scripts/seed_catalogo.sh db/seeds/catalog.sql db/seeds/catalog_lineage.sql
  log "Semillas aplicadas con éxito."
}

desplegar_web() {
  log "Obteniendo URL de karisma-api..."
  local url_api
  url_api=$(gcloud run services describe karisma-api --region="$REGION" --project="$PROYECTO" --format='value(status.url)')
  log "URL API: $url_api"

  log "Desplegando servicio karisma-web en Cloud Run (público)..."
  gcloud run deploy karisma-web \
    --image="$REGION-docker.pkg.dev/$PROYECTO/$REPOSITORIO/web:$ETIQUETA" \
    --region="$REGION" \
    --project="$PROYECTO" \
    --allow-unauthenticated \
    --min-instances=0 \
    --max-instances=3 \
    --memory=512Mi \
    --concurrency=80 \
    --set-env-vars="NUXT_API_BASE=${url_api},NUXT_API_AUDIENCE=${url_api},NUXT_PUBLIC_ENTORNO=demo,NUXT_PUBLIC_DEMO_ACCESO=true" \
    --quiet
  log "karisma-web desplegado."
}

conceder_invocacion() {
  log "Concediendo roles/run.invoker sobre karisma-api a la cuenta de servicio Compute..."
  gcloud run services add-iam-policy-binding karisma-api \
    --region="$REGION" \
    --project="$PROYECTO" \
    --member="serviceAccount:${NUMERO_PROYECTO}-compute@developer.gserviceaccount.com" \
    --role=roles/run.invoker \
    --quiet
  log "Binding IAM concedido."
}

crear_presupuesto() {
  log "Configurando alerta de presupuesto ($45 USD)..."
  if ! gcloud billing budgets list --billing-account="$CUENTA_FACTURACION" --format="value(displayName)" 2>/dev/null | grep -q "Karisma Data 45 USD"; then
    gcloud billing budgets create \
      --billing-account="$CUENTA_FACTURACION" \
      --display-name="Karisma Data 45 USD" \
      --budget-amount=45USD \
      --filter-projects="projects/$NUMERO_PROYECTO" \
      --threshold-rule=percent=0.5 \
      --threshold-rule=percent=0.8 \
      --threshold-rule=percent=1.0 \
      --quiet || log "Aviso: No se pudo crear presupuesto automáticamente (verificar permisos de billing)."
  else
    log "Presupuesto ya existente."
  fi
}

verificar() {
  log "Ejecutando verificación post-despliegue..."
  bash scripts/verificar_despliegue.sh
}

imprimir_resumen() {
  local url_web url_api
  url_web=$(gcloud run services describe karisma-web --region="$REGION" --project="$PROYECTO" --format='value(status.url)' 2>/dev/null || echo "N/A")
  url_api=$(gcloud run services describe karisma-api --region="$REGION" --project="$PROYECTO" --format='value(status.url)' 2>/dev/null || echo "N/A")
  printf "\n=======================================================\n"
  printf " Despliegue completado con éxito (US-M01)\n"
  printf " URL Web (Pública):  %s\n" "$url_web"
  printf " URL API (Privada):  %s\n" "$url_api"
  printf "=======================================================\n\n"
}

ejecutar_fase() {
  local fase="$1"
  case "$fase" in
    apis) habilitar_apis ;;
    registro) crear_registro ;;
    base) crear_base ;;
    secretos) cargar_secretos ;;
    imagenes) construir_imagenes ;;
    api) desplegar_api ;;
    migraciones) aplicar_migraciones ;;
    semillas) aplicar_semillas ;;
    web) desplegar_web ;;
    iam) conceder_invocacion ;;
    presupuesto) crear_presupuesto ;;
    verificar) verificar ;;
    *)
      echo "Fase desconocida: $fase"
      exit 1
      ;;
  esac
}

main() {
  exigir_proyecto
  if [ "$#" -gt 0 ]; then
    for f in "$@"; do
      ejecutar_fase "$f"
    done
  else
    habilitar_apis
    crear_registro
    crear_base
    cargar_secretos
    construir_imagenes
    desplegar_api
    aplicar_migraciones
    aplicar_semillas
    desplegar_web
    conceder_invocacion
    crear_presupuesto
    verificar
  fi
  imprimir_resumen
}

main "$@"
