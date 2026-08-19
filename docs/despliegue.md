# Runbook de Despliegue en GCP — Karisma Data (US-M01)

Este documento describe la arquitectura, prerrequisitos, procedimiento operativo, verificación y reversión del despliegue puente en Google Cloud Platform (GCP) para la plataforma **Karisma Data**.

---

## 1. Arquitectura de Despliegue

```
Navegador del Usuario
  │ (HTTPS público, único origen)
  ▼
Cloud Run [karisma-web] (Público, --allow-unauthenticated)
  │ Nitro Proxy (server/api/[...].ts)
  │  - Authorization: Bearer <JWT de sesión del usuario>
  │  - X-Serverless-Authorization: Bearer <ID token IAM de serviceAccount:compute>
  ▼
Cloud Run [karisma-api] (Privado, --no-allow-unauthenticated)
  │ FastAPI + Polars
  │ Socket Unix: /cloudsql/tareas-computo-nube:us-central1:karisma-pg
  ▼
Cloud SQL [karisma-pg] (PostgreSQL 15 Enterprise, db-f1-micro, Zonal, 10 GB HDD)
```

- **Parquet sintéticos**: 25 MB embebidos directamente en la imagen de `karisma-api` (`stage: runtime-con-datos`).
- **Secretos**: `DATABASE_URL`, `JWT_SECRET_KEY` y `GEMINI_API_KEY` inyectados vía Secret Manager.
- **Sin conector VPC Serverless**: Conexión nativa Cloud Run a Cloud SQL vía `--add-cloudsql-instances`.

---

## 2. Prerrequisitos

1. **Google Cloud SDK (`gcloud`)** instalado y autenticado con credenciales de operador:
   ```bash
   gcloud auth login
   gcloud auth application-default login
   ```
2. **Proyecto activo y región**:
   - Proyecto: `tareas-computo-nube` (Número: `${GCP_PROJECT_NUMBER}`)
   - Facturación: `${GCP_BILLING_ACCOUNT}`
   - Región: `us-central1`
3. **Docker** en ejecución en la máquina local.
4. **Archivo local de configuración**: `backend/.env.local` con las variables de base de datos y llaves.

### Las cuatro variables sin las que el despliegue se detiene

Ninguna tiene valor por omisión, y esa ausencia es deliberada: un valor de ejemplo escrito en el
repositorio deja de ser un ejemplo en cuanto `scripts/desplegar.sh` lo sube a Secret Manager, porque
a partir de ahí es el secreto que firma los tokens del portal público. El guion aborta antes de
crear un solo recurso si falta alguna.

| Variable | De dónde sale | Qué pasa si falta |
|---|---|---|
| `JWT_SECRET_KEY` | `backend/.env.local` | Aborta antes de tocar Secret Manager |
| `GEMINI_API_KEY` | `backend/.env.local` | Idem |
| `KARISMA_DB_PASSWORD` (o `POSTGRES_PASSWORD`) | `backend/.env.local` | Idem; es la contraseña del usuario de Cloud SQL |
| `CUENTA_FACTURACION` (o `GCP_BILLING_ACCOUNT`) | el entorno del operador | Aborta: sin ella no se puede comprobar contra qué cuenta se gasta |

`scripts/verificar_despliegue.sh` exige además `KARISMA_DEMO_PASSWORD`, la contraseña compartida de
los siete usuarios sembrados, por el mismo motivo.

**Si alguna vez se desplegó con un valor de ejemplo**, rotar: `JWT_SECRET_KEY` con una versión nueva
del secreto y un redespliegue, y la contraseña de Cloud SQL con `gcloud sql users set-password`.

---

## 3. Despliegue Automatizado

### Despliegue Completo
```bash
make desplegar
# o directamente:
bash scripts/desplegar.sh
```

### Despliegue por Fases Específicas
El script `scripts/desplegar.sh` admite ejecutar fases individuales:
```bash
bash scripts/desplegar.sh apis registro base secretos imagenes api migraciones semillas web iam presupuesto verificar
```

---

## 4. Verificación Post-Despliegue

Para validar automáticamente los criterios de aceptación CA-5, CA-10 y CA-11:
```bash
make verificar-despliegue
# o directamente:
bash scripts/verificar_despliegue.sh
```

Comprueba:
1. Privacidad del backend: `403 Forbidden` sin ID token IAM; `200 OK` con ID token.
2. Disponibilidad de las rutas públicas (`/`, `/acceso`, `/guia`).
3. Autenticación exitosa de los 7 usuarios sembrados.
4. Cumplimiento de la matriz de permisos por rol (Operativo, Analista, Directivo, Administrador).
5. Respuestas con datos reales en tablero, catálogo y linaje.

---

## 5. Procedimiento de Reversión (Rollback)

En caso de requerir el desmantelamiento total de los recursos creados en GCP:

```bash
# 1. Eliminar servicios Cloud Run
gcloud run services delete karisma-web --region=us-central1 --project=tareas-computo-nube --quiet
gcloud run services delete karisma-api --region=us-central1 --project=tareas-computo-nube --quiet

# 2. Eliminar instancia de Cloud SQL
gcloud sql instances delete karisma-pg --project=tareas-computo-nube --quiet

# 3. Eliminar repositorio Artifact Registry
gcloud artifacts repositories delete karisma --location=us-central1 --project=tareas-computo-nube --quiet

# 4. Eliminar secretos de Secret Manager
gcloud secrets delete DATABASE_URL --project=tareas-computo-nube --quiet
gcloud secrets delete JWT_SECRET_KEY --project=tareas-computo-nube --quiet
gcloud secrets delete GEMINI_API_KEY --project=tareas-computo-nube --quiet

# 5. Eliminar presupuesto de facturación
# Listar y eliminar por ID
gcloud billing budgets list --billing-account="${GCP_BILLING_ACCOUNT}"
```

---

## 6. Estimación de Costos Mensuales

| Recurso | Configuración | Costo Mensual Estimado |
|---|---|---|
| Cloud SQL `karisma-pg` | PostgreSQL 15 `db-f1-micro` + 10 GB HDD | ~$8.00 USD |
| IP Pública Cloud SQL | 1 dirección IPv4 | ~$3.00 USD |
| Cloud Run `karisma-api` & `karisma-web` | Scale-to-zero (0 a 3 instancias, 512 MiB) | $0.00 - $3.00 USD |
| Artifact Registry `karisma` | 2 imágenes con política de 3 versiones | < $1.00 USD |
| Secret Manager | 3 secretos | < $0.50 USD |
| **Total Estimado** | | **~$13.00 - $16.00 USD/mes** |

*El presupuesto configurado en GCP fija alertas al 50% ($22.50 USD), 80% ($36.00 USD) y 100% ($45.00 USD).*
