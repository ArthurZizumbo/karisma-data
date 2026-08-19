#!/usr/bin/env bash
# ===========================================================================
# Karisma Data — Verificación post-despliegue en GCP (US-M01)
#
# Comprueba:
#   1. Privacidad de API: 403 sin token IAM, 200 con token IAM (CA-5).
#   2. Rutas del frontend público responden (200).
#   3. Inicio de sesión para los 7 usuarios sembrados (POST /api/auth/token).
#   4. Matriz de permisos por rol (rutas permitidas 200, prohibidas 403).
#   5. Endpoints de datos responden con contenido (CA-11).
# ===========================================================================
set -euo pipefail

PROYECTO="${PROYECTO:-tareas-computo-nube}"
REGION="${REGION:-us-central1}"

# Sin valor por omision: la contrasena de los siete usuarios sembrados es la
# puerta de la demostracion publica y escribirla aqui la publica con el
# repositorio. Sale de backend/.env.local, que git ignora.
KARISMA_DEMO_PASSWORD="${KARISMA_DEMO_PASSWORD:-${POSTGRES_PASSWORD:-}}"

# Las URL se preguntan a gcloud y no se escriben: una direccion de Cloud Run
# lleva el identificador del proyecto y cambia si el servicio se recrea, asi que
# un valor de respaldo escrito aqui envejece y ademas publica ese identificador.
URL_WEB="${URL_WEB:-$(gcloud run services describe karisma-web --region="$REGION" --project="$PROYECTO" --format="value(status.url)" 2>/dev/null || true)}"
URL_API="${URL_API:-$(gcloud run services describe karisma-api --region="$REGION" --project="$PROYECTO" --format="value(status.url)" 2>/dev/null || true)}"

log() {
  printf "\n\033[1;32m[VERIFICAR]\033[0m %s\n" "$*"
}

error() {
  printf "\n\033[1;31m[FALLO]\033[0m %s\n" "$*" >&2
  exit 1
}

if [ -z "$URL_WEB" ] || [ -z "$URL_API" ]; then
  error "No se pudieron obtener las URLs de karisma-web y karisma-api. Autentica gcloud o pasalas en URL_WEB y URL_API."
fi

if [ -z "$KARISMA_DEMO_PASSWORD" ]; then
  error "Falta KARISMA_DEMO_PASSWORD. Sale de backend/.env.local; este guion no trae ninguna contrasena escrita."
fi

log "URL Web: $URL_WEB"
log "URL API: $URL_API"

TMP_DIR="$(mktemp -d 2>/dev/null || mktemp -d -t 'karisma_test')"
trap 'rm -rf "$TMP_DIR"' EXIT

# 1. Comprobar aislamiento de API (CA-5)
#
# Las dos mitades fallan, y esa es la razon de ser de esta seccion. Una version
# anterior avisaba y seguia: con el backend abierto a internet el guion llegaba
# igual a su mensaje de exito, de modo que el unico criterio que esta US existe
# para sostener era tambien el unico que no podia ponerse rojo.
log "1. Comprobando aislamiento de karisma-api..."
status_anon=$(curl -s -o /dev/null -w "%{http_code}" "$URL_API/health" || true)
if [ "$status_anon" != "403" ]; then
  error "karisma-api respondio $status_anon sin identidad y debia responder 403: el backend no esta cerrado."
fi
log "Aislamiento verificado: API devuelve 403 sin token IAM."

id_token=$(gcloud auth print-identity-token 2>/dev/null || gcloud.cmd auth print-identity-token 2>/dev/null || true)
if [ -z "$id_token" ]; then
  error "No se pudo obtener un ID token con gcloud. Sin el, la otra mitad de CA-5 queda sin comprobar."
fi
status_iam=$(curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $id_token" "$URL_API/health" || true)
if [ "$status_iam" != "200" ]; then
  error "API no respondió 200 con ID token IAM (código: $status_iam)."
fi
log "API respondió 200 con ID token IAM."

# 2. Comprobar rutas del frontend público
log "2. Comprobando rutas públicas en karisma-web..."
rutas_publicas=(
  "/"
  "/acceso"
  "/guia"
)

for r in "${rutas_publicas[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "$URL_WEB$r")
  if [ "$code" != "200" ]; then
    error "Ruta $r devolvió HTTP $code en $URL_WEB"
  fi
  echo "  ✓ $r -> 200"
done

# 3. Comprobar inicio de sesión de los 7 usuarios sembrados
log "3. Comprobando autenticación de los 7 usuarios..."
usuarios=(
  "movalle:admin"
  "lmendez:operativo"
  "eruiz:operativo"
  "dhernandez:analista"
  "jmendieta:analista"
  "acastaneda:directivo"
  "rvaldez:directivo"
)

for entry in "${usuarios[@]}"; do
  u="${entry%%:*}"
  r="${entry##*:}"
  cookie_file="$TMP_DIR/cookie_$u.txt"
  
  resp=$(curl -s -c "$cookie_file" -b "$cookie_file" -X POST "$URL_WEB/api/auth/token" \
    -H "Content-Type: application/json" \
    -d "{\"usuario\":\"$u\",\"contrasena\":\"$KARISMA_DEMO_PASSWORD\"}")
  
  if ! echo "$resp" | grep -q "\"usuario\":\"$u\""; then
    error "No se pudo autenticar usuario $u: $resp"
  fi
  echo "  ✓ $u ($r) -> autenticado con éxito"
done

# 4. Comprobar matriz de visibilidad y permisos por rol
log "4. Comprobando matriz de permisos por rol..."
cookie_op="$TMP_DIR/cookie_lmendez.txt"
cookie_an="$TMP_DIR/cookie_dhernandez.txt"
cookie_adm="$TMP_DIR/cookie_movalle.txt"

# Operativo: puede usar /api/catalog/search, NO puede /api/metrics/series ni /api/users
code_op_ok=$(curl -s -o /dev/null -w "%{http_code}" -b "$cookie_op" "$URL_WEB/api/catalog/search?q=cartera")
code_op_forb=$(curl -s -o /dev/null -w "%{http_code}" -b "$cookie_op" "$URL_WEB/api/metrics/series?metrica=saldo_disponible_mxn&formato=json")
if [ "$code_op_ok" != "200" ] || [ "$code_op_forb" != "403" ]; then
  error "Fallo en permisos de Operativo (catalog: $code_op_ok [esperado 200], series: $code_op_forb [esperado 403])"
fi
echo "  ✓ Operativo: permisos correctos (catalog 200, metrics 403)"

# Analista: puede /api/metrics/series, NO puede /api/users
code_an_ok=$(curl -s -o /dev/null -w "%{http_code}" -b "$cookie_an" "$URL_WEB/api/metrics/series?metrica=saldo_disponible_mxn&formato=json")
code_an_forb=$(curl -s -o /dev/null -w "%{http_code}" -b "$cookie_an" "$URL_WEB/api/users")
if [ "$code_an_ok" != "200" ] || [ "$code_an_forb" != "403" ]; then
  error "Fallo en permisos de Analista (series: $code_an_ok [esperado 200], users: $code_an_forb [esperado 403])"
fi
echo "  ✓ Analista: permisos correctos (metrics 200, users 403)"

# Admin: puede /api/users
code_adm_ok=$(curl -s -o /dev/null -w "%{http_code}" -b "$cookie_adm" "$URL_WEB/api/users")
if [ "$code_adm_ok" != "200" ]; then
  error "Fallo en permisos de Admin (users: $code_adm_ok [esperado 200])"
fi
echo "  ✓ Admin: permisos correctos (users 200)"

# 5. Comprobar endpoints de datos con contenido real (CA-11)
log "5. Comprobando respuesta de endpoints de datos (CA-11)..."
# Catálogo
res_cat=$(curl -s -b "$cookie_an" "$URL_WEB/api/catalog/search?q=cartera")
if ! echo "$res_cat" | grep -q "total"; then
  error "Búsqueda en catálogo no devolvió contenido esperado: $res_cat"
fi
echo "  ✓ Catálogo respondió con resultados"

# Series
res_series=$(curl -s -b "$cookie_an" "$URL_WEB/api/metrics/series?metrica=saldo_disponible_mxn&formato=json")
if ! echo "$res_series" | grep -q "valores"; then
  error "Serie de métricas no devolvió datos: $res_series"
fi
echo "  ✓ Series de métricas respondió con datos reales"

log "¡TODAS LAS VERIFICACIONES COMPLETADAS EXITOSAMENTE!"
