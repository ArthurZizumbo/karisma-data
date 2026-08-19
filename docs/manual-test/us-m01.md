# Pruebas manuales — US-M01 (Despliegue puente en GCP con base administrada)

**SHA base**: `f06acee` · **Rama**: `us-m01` · **Fecha de este documento**: 19-ago-2026

Aquí está solo lo que la suite **no** puede demostrar. Las 1 072 pruebas del frontend y las 828 del
backend doblan `$fetch`, el evento de h3 y el sistema de archivos: ninguna abre un socket contra
Cloud Run, ninguna conoce una política de IAM y ninguna puede ver un arranque en frío. Lo que sí es
mecánico —la traducción del DSN, la caché del ID token, las cabeceras del proxy— ya lo cubre
`make test` y **no se repite aquí**.

> **Corrección del 19-ago-2026.** La versión anterior de este documento registraba el recorrido de
> los cuatro roles con las cuentas `patricia.operaciones@karisma.com`, `sofia.analitica@karisma.com`,
> `carlos.direccion@karisma.com` y `admin.sistema@karisma.com`. **Ninguna de las cuatro existe**: los
> siete usuarios sembrados por `db/migrations/20260811211250_create_app_user.sql` son `movalle`,
> `lmendez`, `eruiz`, `dhernandez`, `jmendieta`, `acastaneda` y `rvaldez`, con correos
> `@karisma.demo`. Un recorrido marcado PASS contra credenciales inexistentes no es evidencia de
> nada, así que se reescribió entero con los usuarios reales y se rehízo lo automatizable.

---

## Estado de ejecución

**Ejecutado por comando el 19-ago-2026** contra el despliegue vivo, dentro del QA de esta US. Lo
verificado sin navegador está en la tabla siguiente; lo que exige ojo humano queda como pasos
pendientes en la sección 3, sin marcar.

| Comprobación | Comando | Resultado |
|---|---|---|
| Aislamiento del backend | `curl -o /dev/null -w '%{http_code}' $URL_API/health` | **403** — la API no responde sin identidad |
| Frontend público | `curl -o /dev/null -w '%{http_code}' $URL_WEB/` | **200** |
| Los siete usuarios entran por la URL pública | `POST $URL_WEB/api/auth/token` con cada uno | **200 los siete** |
| Matriz por rol, `operativo` (`lmendez`, `eruiz`) | `GET /api/catalog/search`, `/api/metrics/series`, `/api/users` | **200 / 403 / 403** |
| Matriz por rol, `analista` (`dhernandez`, `jmendieta`) | idem | **200 / 200 / 403** |
| Matriz por rol, `directivo` (`acastaneda`, `rvaldez`) | idem | **200 / 200 / 403** |
| Matriz por rol, `admin` (`movalle`) | idem | **200 / 200 / 200** |
| Cloud SQL | `gcloud sql instances describe karisma-pg` | `POSTGRES_15 ENTERPRISE db-f1-micro ZONAL 10 PD_HDD False False` |
| Escalado de ambos servicios | `gcloud run services describe` | `max=3`, `concurrency=80`, `512Mi`; `minScale` ausente = 0 |
| Secretos | `gcloud run services describe karisma-api` | los tres por `secretKeyRef`; ninguno en claro |
| Artifact Registry | `gcloud artifacts repositories describe karisma` | `KEEP` con `keepCount: 3` + `DELETE` del resto |

---

## 1. Lo que solo se ve en un navegador real

| Paso a paso | Resultado esperado |
|---|---|
| 1. Abrir `$URL_WEB/` en una ventana nueva, sin sesión previa, con la consola abierta | La portada pinta completa, con la franja de alcance visible. **Cero errores y cero avisos de hidratación** en consola |
| 2. Cronometrar ese primer arranque tras ≥15 min de inactividad de los servicios | El tiempo hasta el primer pintado se anota. Es el arranque en frío de `min-instances 0` y es el número que la prueba SUS de A5 va a sentir; si supera ~10 s, se decide `min-instances 1` **solo** el día de la prueba y se revierte después |
| 3. Entrar en `/acceso` con `lmendez` y la contraseña de demostración | Aterriza en `/inicio`. En Aplicación → Cookies, la de sesión es `HttpOnly`, `Secure` y `SameSite=Strict`, y **no** aparece ningún JWT en `localStorage` ni en el cuerpo de la respuesta |
| 4. Con esa sesión, escribir `/administracion` en la barra de direcciones | **HTTP 403 real** con el estado diseñado, no un 200 con pantalla de disculpa. La barra lateral no muestra Administración |
| 5. Recorrer `/inicio`, `/exploracion`, `/exploracion/tableros` y `/gobierno` con la sesión `dhernandez` | Los tableros pintan **puntos reales** —los Parquet viajan dentro de la imagen del backend—, el catálogo devuelve fuentes y campos, y el linaje abre su superposición. Ninguna pantalla en vacío |
| 6. Cambiar a inglés desde la cabecera en cualquiera de esas pantallas | Traduce todo, incluidos los nombres de rol interpolados. La URL no cambia |
| 7. Entrar como `movalle` y abrir `/administracion` | La tabla lista los **siete** usuarios sembrados con su rol |

## 2. Lo que exige juicio sobre el despliegue

| Paso a paso | Resultado esperado |
|---|---|
| 8. Revisar en la consola del navegador la pestaña Red durante el paso 5 | **Ninguna petición sale hacia el dominio de `karisma-api`**: el navegador solo habla con el origen del frontend. Es la mitad de CA-5 que ningún `curl` demuestra |
| 9. Solicitar una exportación en `/exploracion/exportar` y descargarla | El trabajo llega a completado y el enlace descarga el archivo. **Anotar si falla**: con `EXPORT_STORAGE_BACKEND=local` y `max-instances 3`, un trabajo creado en una instancia y descargado desde otra da enlace muerto. El riesgo está declarado en §10 R3 del plan y su salida es el bucket de GCS |
| 10. Abrir `/asistente` y enviar una pregunta | Responde el guion determinista con su franja de honestidad visible. La franja **no se recorta**: `CHAT_PROVIDER=guionizado` en el despliegue |
| 11. Comprobar en la consola de facturación que la alerta de presupuesto está activa | Existe «Karisma Data 45 USD» sobre el proyecto, con umbrales 50 %, 80 % y 100 %. **Ojo**: el monto quedó fijado en **900 MXN**, porque la cuenta factura en pesos y `gcloud` convirtió los 45 USD al crearlo. Equivale al techo pedido hoy; si el tipo de cambio se mueve, el techo en dólares deriva y hay que reajustarlo a mano |

## 3. Antes de reclutar participantes para A5

| Paso a paso | Resultado esperado |
|---|---|
| 12. Repetir el paso 3 desde una red distinta a la del equipo (datos móviles) | Entra igual. Descarta que algo dependa de la máquina que desplegó |
| 13. Abrir la URL en un teléfono | El portal es de escritorio por decisión de diseño; se anota qué se rompe para no descubrirlo con un participante delante |
| 14. Dejar el portal sin usar 20 minutos y volver a entrar | La sesión sigue viva o expira con el rebote a `/acceso` y su motivo; nunca una pantalla en blanco |

---

## Lo que este documento no puede afirmar

- **Que `dbmate up` se ejecutó contra Cloud SQL en este árbol**: el QA no levantó el Auth Proxy. Lo
  que sí consta es que `db/schema.sql` no tiene diferencias contra el repositorio y que el portal
  desplegado responde con datos, lo que exige un esquema aplicado y las semillas cargadas.
- **Que el cierre por IAM tardó menos de 45 minutos** (CA-5b): eso lo declara `ADR-004`, no una
  medición de esta pasada. Lo verificable es el resultado —403 sin identidad—, y está verificado.
