# ADR-004: Cierre por IAM de Cloud Run y su Salida Declarada

**Estado**: Aceptado y Verificado (Rama A — Cierre estricto por IAM) · **Fecha**: 18-ago-2026 · **US**: US-M01

## Contexto y Problema

El portal Karisma Data expone su frontend mediante el servicio Cloud Run `karisma-web` (público) y su API FastAPI mediante `karisma-api`.
La arquitectura de seguridad de la solución establece que el navegador solo habla con el origen único del frontend (`karisma-web`), que actúa como proxy inverso en `/api/**` hacia `karisma-api`.

Para impedir el acceso no autenticado o directo al backend desde internet (CA-5), `karisma-api` se despliega como servicio privado con `--no-allow-unauthenticated`.
Sin embargo, `Authorization` ya transporta el JWT de sesión del usuario (que gobierna los scopes y la autorización por rol en la API). Para invocar el servicio privado sin pisar dicho JWT, Cloud Run admite la cabecera `X-Serverless-Authorization: Bearer <id_token>`, la cual es consumida y retirada por la infraestructura de Cloud Run antes de entregar la petición a FastAPI.

## Criterio de Tiempo y Puerta de Salida (CA-5b)

El enlace de permisos IAM (`roles/run.invoker` sobre `karisma-api` concedido a la cuenta de servicio de `karisma-web`) puede demorar por propagación de IAM o políticas organizacionales de GCP.
Se define un límite estricto de **45 minutos** desde el primer intento de `add-iam-policy-binding`.

### Rama A (Cierre Exitoso por IAM - Invocación Privada)
- `karisma-api` permanece con `--no-allow-unauthenticated`.
- `karisma-web` obtiene un token de identidad OIDC de la cuenta de servicio desde el servidor de metadatos de Cloud Run (`http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/identity?audience=$URL_API`) con cabecera `Metadata-Flavor: Google`.
- El token de identidad viaja en `X-Serverless-Authorization`.
- El JWT de sesión del usuario viaja intacto en `Authorization`.
- Petición directa a `$URL_API/health` sin token IAM devuelve **403 Forbidden**.
- Petición a través del proxy de `$URL_WEB/api/health` devuelve **200 OK**.

### Rama B (Salida de Emergencia por Agotamiento de Ventana >45 min)
- `karisma-api` se redespliega con `--allow-unauthenticated`.
- **No se relaja ningún scope de datos**: todo endpoint de negocio (`/api/catalog/**`, `/api/metrics/**`, `/api/export/**`, etc.) continúa exigiendo `Security(get_current_user, scopes=[...])`.
- Lo único alcanzable anónimamente son los endpoints públicos por diseño (`/health`, `/api/auth/token`, `/api/auth/demo`, `/openapi.json`).
- Queda registrada la deuda técnica para resolver el binding de IAM en una iteración posterior.

---

## Registro de Ejecución

- **Hora de inicio del binding IAM**: 18-ago-2026 23:21:46 CST
- **Hora de verificación exitosa**: 18-ago-2026 23:30:11 CST (<9 minutos)
- **Rama ejecutada**: **Rama A** (Cierre estricto por IAM verificado)
- **Evidencia**: `bash scripts/verificar_despliegue.sh` pasó todas las pruebas (aislamiento 403, invocación OIDC 200, 7 usuarios autenticados, matriz de roles y datos reales).
