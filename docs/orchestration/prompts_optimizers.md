# Prompts Optimizados — Karisma Data

Flujo de siete fases para ejecutar una User Story con agentes.

**Cómo usar**: escribe `Fase N — US-XXX: [título]` y pega el prompt de esa fase.
El orquestador de Fase 3 lanza subagentes en paralelo; no abres sesiones nuevas. La única
excepción es Fase 5, que por ser diálogo largo conviene aparte.

Este documento no repite lo que ya vive en otro lado:

| Necesitas | Está en |
|-----------|---------|
| El texto de la US, sus criterios y su estimación | [`context/planeacion_proyecto.md`](../../context/planeacion_proyecto.md) — única fuente de verdad |
| Qué skill cargar antes de cada acción | [`auto-invoke.md`](auto-invoke.md) |
| Las reglas de código de una capa | El `AGENTS.md` de esa carpeta |
| Las reglas transversales | Raíz — **ya cargadas, no hay que leerlas** |
| Revisar defectos de interfaz | [`checklist-ui.md`](checklist-ui.md) |

> **Sobre `AGENTS.md` y `CLAUDE.md`.** En la raíz son **espejos byte-idénticos**, y Claude Code
> carga el de raíz solo en cada sesión: **pedirle a un agente que lo lea son ~2,300 tokens
> tirados**. En las carpetas **solo existe `AGENTS.md`** — no hay `backend/CLAUDE.md` ni
> equivalentes—, así que los prompts dicen `AGENTS.md` y apuntan a un archivo que sí existe.

### De dónde sacar el bloque de la US

Se busca por el encabezado `### US-XXX`, nunca por número de línea: las líneas se mueven con
cada edición, el encabezado no.

**Hoy hay US que aparecen dos veces**, y la regla de desempate importa:

| Dónde | Qué contiene | Cuándo se usa |
|-------|--------------|---------------|
| **§26.2 Avance 4** | 19 bloques con el **alcance recortado de S4** y el sufijo `(alcance S4)` en el título | Del 10 al 16 de agosto. **Manda sobre §11–§17** |
| **§11 a §17, por EPIC** | El alcance de **producción** de las 41 US + US-UX-01..09 | Fuera de esa ventana, y siempre para saber a qué aspira la US al final |

Dieciocho de los diecinueve bloques de §26.2 tienen su gemelo en un EPIC —`US-008` está en §13 y
en §26.2, `US-015` en §14 y en §26.2, y así—. Si un agente hace `grep "### US-008"` y encuentra
dos resultados, **toma el que trae `(alcance S4)` mientras estemos en la semana**, y el del EPIC
después.

Cuando pase S4, §26 queda como registro histórico de la semana y el flujo vuelve a §11–§17 sin
tocar nada. Si una semana futura necesita su propio contrato recortado, se añade §27 con el mismo
patrón: preámbulo, recálculo de capacidad, bloques con sufijo de alcance, y la misma regla de
precedencia.

---

## Presupuesto de lectura por agente

La idea que sostiene el ahorro: **el handoff es el portador de contexto, no los documentos.**
Cada agente lee lo mínimo para hacer su parte y escribe en el handoff lo que el siguiente
necesita saber. Nadie relee el repositorio.

| Fase | Lee | NO lee |
|------|-----|--------|
| 2 Planeación | El bloque de la US · el `AGENTS.md` de la carpeta · `grep` dirigido | El plan completo · guías de otras capas |
| 3 cada subagente | Su `AGENTS.md` · el handoff · las secciones 3-4 del planning | El planning completo · las guías de capas ajenas · la raíz |
| 4 QA | El handoff · **solo los archivos del diff** | El repositorio |
| 5 Correcciones | El handoff · el manual-test · el diff | Los `AGENTS.md`, salvo que el handoff diga que algo se salió del estándar |
| 6 QA final | La sección "Bugs resueltos" · el diff | Todo lo demás |
| 7 Cierre | El handoff | Todo lo demás |

**Context7 es caro** (de 5k a 20k tokens por consulta): se usa **solo cuando la API es
genuinamente desconocida o cambió de versión**. Con el stack congelado eso casi nunca pasa. No se
consulta "por si acaso" ni por una lista de librerías.

**Y la trampa contraria, que conviene decir sin adornos:** el fan-out **no ahorra tokens totales**,
gasta más que un agente secuencial. Lo que compra es tiempo de reloj y contexto limpio — ocho
contextos de 3k rinden mejor que uno de 200k degradándose. Si la US es chica o si el objetivo es
gastar poco, **no repartas: hazla secuencial**. Reparte cuando el reloj apriete o cuando las capas
sean de verdad independientes.

---

## Dominio → subagente

Los nueve viven en `.claude/agents/`. Es el mapa que usa el fan-out de la Fase 3.

| Dominio | Subagente | Carpeta |
|---------|-----------|---------|
| backend | `backend-engineer` | `backend/` |
| frontend | `frontend-engineer` | `frontend/` |
| datos, silos, migraciones | `data-engineer` | `ml/`, `db/`, `data/` |
| agente conversacional | `agent-engineer` | `ml/agent/` |
| infra, Docker, CI, OTel | `platform-engineer` | raíz, `infra/`, `.github/` |
| entregable del curso | `deliverable-writer` | `docs/entregables/` |
| investigación y pre-validación UX | `ux-researcher` | `docs/entregables/`, `datos/` |
| auditoría de seguridad | `security-reviewer` | transversal, solo lectura |
| costo | `finops-auditor` | transversal, solo lectura |

---

## La nube, en la práctica

No hay GPU ni entrenamiento. El cómputo es serverless: dos Cloud Run con escalado a cero y una
Cloud SQL mínima, en el proyecto `tareas-computo-nube`, región `us-central1`.

**Desplegar** — el escalado a cero hace que no cueste fuera de uso:

```bash
gcloud run deploy karisma-api --source backend  --region us-central1
gcloud run deploy karisma-web --source frontend --region us-central1
```

**Migrar contra la nube.** dbmate no habla el socket de Cloud SQL: se levanta el proxy y se apunta
a `127.0.0.1`.

```bash
cloud-sql-proxy tareas-computo-nube:us-central1:karisma-pg --port 5432 &
DATABASE_URL="postgres://karisma_app:<pass>@127.0.0.1:5432/karisma?sslmode=disable" dbmate up
```

**Ver qué revisión está sirviendo:**

```bash
gcloud run services describe karisma-api --region us-central1 \
  --format='value(status.url,status.latestReadyRevisionName)'
```

Tres cosas que muerden:

- **Confirmar el proyecto activo** antes de escribir nada: existe otro proyecto llamado
  `karisma-data`, sin facturación, y desplegar ahí falla de formas confusas.
  `gcloud config get-value project`.
- **El shell es Windows.** Git Bash y PowerShell conviven, pero los heredocs y `$VAR` son de Bash.
  Para algo multilínea, un archivo `.ps1` o `.sh`, no una cadena con `;`.
- **Una migración aplicada no se edita.** Se corrige hacia adelante con otra.

---

## Template Handoff

Cada subagente crea o actualiza `docs/us-handoff/us-XXX.md` al entrar y al salir. Es el archivo
que evita que el siguiente agente relea el repositorio.

```markdown
# Handoff US-XXX — [Titulo]

**Estado**: planning | coding | qa | testing | ready-to-close
**Epic**: EPIC UX | E0 | E1 | E2 | E3 | E4 | E5
**Actividad**: A{N} ([fecha de entrega])
**Sprint**: S{N}
**Rama**: feature/E{epic}-US-XXX-{slug}
**SHA base**: [git rev-parse HEAD ANTES de programar — ancla del diff; lo escribe Fase 3]
**Ultima fase**: [N — fecha]

## Dominios y sub-tareas tocados
- [ ] backend  - [ ] frontend  - [ ] ml  - [ ] agent  - [ ] infra  - [ ] db  - [ ] docs
- Sub-tareas paralelas: [ej. front/A inicio, front/B exploracion, front/C gobierno]

## Archivos tocados
- `backend/app/api/catalog.py` — router nuevo

## Archivos existentes reutilizados
- `backend/app/utils/pagination.py` — se extendio, no duplicar

## Decisiones tecnicas clave
- Se uso X en vez de Y porque Z

## Bugs resueltos
| Bug | Causa | Solucion | Estado |
|-----|-------|----------|--------|

## Zonas sensibles
- `frontend/app/assets/css/main.css` — GENERADO por script; no editar a mano

## Nube y datos
- Revision de Cloud Run desplegada: [karisma-api-000XX / N/A]
- Migracion dbmate aplicada: [nombre / N/A] — schema.sql actualizado: [si/no]

## Llave de provenance (cierre)
> Formato fijo: `US-XXX @ <git_sha7> + run:<revision|-> + db:<migracion|->`
- `US-XXX @ ________ + run:________ + db:________`

## engram-memory
- Observaciones guardadas: [si/no + keywords]
```

---

## Verdict Envelope — gate de QA

Cada QA termina emitiendo este sobre. Reemplaza el "se ve bien, ciérralo" por evidencia
obligatoria.

```json
{
  "check_id": "us-XXX-qa",
  "result": "ok | warn | blocked",
  "evidence": [
    "ruff + mypy: limpio (no hay Makefile todavia, se corrieron directo)",
    "pytest: 142 passed, cobertura backend 78%",
    "matriz 401/403 por rol: 8 casos en verde",
    "gcloud run services describe: revision karisma-api-00014 sirviendo trafico"
  ],
  "why": "todos los criterios de aceptacion verificados contra el codigo del diff",
  "safe_next_step": "Fase 7 cierre directo",
  "requires_confirmation": false
}
```

**Regla de oro**: prohibido `result: "ok"` con `evidence: []` vacío. Sin evidencia citable el
resultado es `blocked`. `warn` pasa con deuda anotada en `why`.

**Y una regla propia de este repo**: el `Makefile` todavía no existe. Si un comando no corre, se
corre la herramienta directamente y **se dice en la evidencia**. Inventar la salida de un comando
inexistente es peor que declarar `blocked`.

---

## Fase 1 — Research
> Solo si la US trae tecnología o patrón nuevo. Con el stack congelado por decisión de equipo,
> la mayoría se la salta.

```text
Investiga para la US-XXX: [titulo].

1. mem_search "[titulo + tecnologia]" ANTES de investigar desde cero.
2. Lee el bloque de la US en context/planeacion_proyecto.md.
3. Separa lo que requiere research real de lo que ya esta decidido en el plan.
4. Solo si la API es desconocida o cambio de version: Context7, luego web search.
5. Carga las skills que docs/orchestration/auto-invoke.md indique para el dominio.
6. Guarda hallazgos en docs/us-research/us-XXX.md.
7. Crea docs/us-handoff/us-XXX.md con el template.

Solo investiga. No planees ni programes.
```

---

## Fase 2 — Planeacion

```text
Planifica la US-XXX: [titulo].

Descripcion:
"""
[Pegar el bloque completo de la US. Buscar "### US-XXX" en context/planeacion_proyecto.md
 y aplicar la regla de desempate de "De donde sacar el bloque de la US": si hay dos
 resultados, gana el que trae "(alcance S4)" mientras estemos en la semana del 10 al 16.
 El bloque son las cuatro partes: Como/quiero/para que + Criterios de Aceptacion +
 Tareas tecnicas + Estimacion]
"""

Lee, y nada mas:
1. docs/us-handoff/us-XXX.md si existe
2. El AGENTS.md de la carpeta que toca — NO el de la raiz, ese ya esta cargado
3. mem_search "[titulo]"
4. docs/us-resolved/ solo si existe una US parecida que valga la pena copiar

Carga las skills que corresponda segun docs/orchestration/auto-invoke.md.
Context7 SOLO si vas a usar una API que no conoces o que cambio de version.

Antes de planear, entiende que YA existe — Grep antes que Read:
- grep -r "[keyword]" backend/app/ frontend/app/ ml/ -l
- ls db/migrations/ | tail -5
- ls frontend/app/components/

DESCOMPOSICION EN SUB-TAREAS PARALELAS:
Si la US tiene tareas independientes en el MISMO dominio, marca como paralelizarlas con
write-sets DISJUNTOS: cada agente escribe archivos distintos.
Solo separa lo que no comparte archivos de escritura. Lo que uno lee y otro escribe va
SECUENCIAL, y el que escribe va primero.
Si la US es chica, di explicitamente que NO se reparte: un agente secuencial gasta menos.

Genera docs/us-planning/us-XXX.md con:
1. Criterios de aceptacion con metricas verificables
2. Arquitectura de la solucion, flujo de capas
3. Archivos exactos a crear o modificar
4. Firmas publicas de cada modulo nuevo
5. Dominios + SUB-TAREAS, con el write-set disjunto de cada agente:
   [ ] backend  [ ] frontend  [ ] ml  [ ] agent  [ ] infra  [ ] db  [ ] docs
6. Plan de tests (backend >=70%, frontend >=50%)
7. Si toca la nube: que comando, sobre que recurso
8. Si toca schema: la migracion y su rollback
9. Si es entregable: a que rubro de la rubrica responde
10. Riesgos y mitigaciones
11. Checklist de cierre

Actualiza el handoff con estado "planning". No programes nada.
```

---

## Fase 3 — Programacion (orquestador con fan-out)

> Tú escribes este prompt. Claude lanza los subagentes; no abres sesiones nuevas.
> **Dos agentes nunca escriben el mismo archivo.**

```text
Programa la US-XXX: [titulo].

Lee:
1. docs/us-handoff/us-XXX.md
2. docs/us-planning/us-XXX.md — seccion 5 "Dominios + sub-tareas" y secciones 3-4

ANTES de programar: git rev-parse HEAD -> escribe el sha7 en el campo "SHA base" del handoff.
Ese sha ancla el diff para las fases siguientes; QA usa git diff --name-only <sha_base>,
nunca HEAD~N.

Lanza subagentes con run_in_background, segun el mapa "Dominio -> subagente":
- 1 agente por dominio marcado en el plan.
- Varios del mismo dominio si el plan lista sub-tareas con write-sets disjuntos.
- Si un agente GENERA algo que otros consumen (tokens de diseno, un schema, un tipo
  compartido), ese va PRIMERO y SOLO. Los demas lo leen, no lo escriben.
- Pares dependientes: secuenciales.
- Si el plan dice que la US no se reparte, hazla tu secuencialmente.

PLANTILLA POR AGENTE:
  "Implementa [dominio/sub-tarea] de la US-XXX: [titulo].
   Lee <carpeta>/AGENTS.md — ahi estan tus reglas. NO leas el de la raiz: ya lo tienes.
   Lee docs/us-handoff/us-XXX.md y las secciones 3-4 de docs/us-planning/us-XXX.md.
   TUS ARCHIVOS (write-set disjunto, no toques otros): [lista exacta del plan].
   Antes de crear: revisa lo existente en TU carpeta; el plan dice que reutilizar.
   Context7 solo si vas a usar una API que no conoces.
   Todo funcional, cero stubs ni TODOs.
   Al terminar: linters y tests de tu capa. Escribe en el handoff tus archivos y tus
   decisiones — es lo unico que vera el siguiente agente."

TRAMPAS POR CAPA
> Lo demas esta en el AGENTS.md de cada carpeta y no se repite aqui. Estas son las que un
> subagente equivoca aunque lo haya leido, porque contradicen lo que suele ser correcto.

- frontend: **i18n esta PROHIBIDO.** La UI es solo en espanol, strings directos en el template.
  Nada de useI18n(), t('key') ni locales. Y `app/assets/css/main.css` es GENERADO: los colores
  y espaciados salen de sus tokens, jamas escritos a mano.
- backend: las consultas analiticas pasan SOLO por la capa semantica. El LLM y el cliente
  componen consultas estructuradas; solo el compilador determinista genera expresiones Polars.
- ml: la semilla es fija y compartida. Si cambia, `make data` deja de reproducir y las consultas
  de referencia dejan de cuadrar.
- agent: toda cifra proviene de un tool call y cita su fuente. Sin tool call no se muestran
  numeros, aunque el modelo "sepa" la respuesta.
- db: jamas `SQLModel.metadata.create_all()`. Solo dbmate, y las contrasenas de seed
  prehasheadas con Argon2.
- infra: Terraform esta congelado; el puente es `gcloud run deploy`. El Makefile no puede usar
  `$(shell ...)` en tiempo de parseo.
- docs: `a1_*`, `a2_*`, `a3_*` y los PDF de `docs/semana_1..3` son entregables ya calificados.
  No se tocan. Y nada se escribe en tiempo futuro.

Cuando todos terminen:
- Integra y resuelve conflictos entre capas: schemas Pydantic compartidos backend<->tools,
  tipos del frontend contra la API, firmas compartidas de ml.
- mem_save con las decisiones tecnicas del run.
- Lanza subagente TESTS en foreground:

TESTS:
  "Escribe los tests faltantes de la US-XXX. Lee docs/us-handoff/us-XXX.md.
   Mockea SIEMPRE Gemini, GCS y Cloud SQL.
   Testea solo los archivos nuevos o modificados de esta US.
   Backend: pytest + pytest-asyncio, con la matriz 401/403 por rol si toco auth.
   Frontend: vitest + Vue Test Utils.
   Si toco SSE: verifica que la cancelacion no deja tareas colgadas."

Actualiza el handoff con el snapshot de archivos y decisiones.
Si desplegaste, anota la revision. Si migraste, anota la migracion.
Reporta git status --short.
```

---

## Fase 4 — QA y Testing

```text
QA de la US-XXX: [titulo].

Lee docs/us-handoff/us-XXX.md PRIMERO.

git diff --name-only <sha_base>   (campo "SHA base" del handoff)
Trabaja SOLO sobre esos archivos. No leas el resto del repositorio.

1. Linters y secrets-scan. Si el Makefile ya existe: make check && pnpm lint.
   Si no: corre ruff, mypy y eslint directamente Y DILO en la evidencia.
2. Tests con cobertura de los archivos del diff: backend >=70%, frontend >=50%.
3. Auditoria de seguridad sobre el diff (skill o subagente security-reviewer).
4. Revision de codigo sobre el diff: DRY, separacion de capas, y las trampas de la Fase 3.
5. Skills adicionales segun lo que toque — ver docs/orchestration/auto-invoke.md.
6. Si toca interfaz: los cuatro estados no felices (vacio, cargando sin salto de maquetacion,
   error, sin permiso) + docs/orchestration/checklist-ui.md.
7. Revisa cada criterio de aceptacion del handoff contra el codigo real.
8. mem_search "[keyword]" por bugs similares previos.

Genera docs/manual-test/us-XXX.md:
  - Formato: [Paso a paso] -> [Resultado esperado]
  - Solo lo que exija navegador real, la URL desplegada o juicio humano
  - La verificacion visual se puede automatizar con el MCP de Playwright

Actualiza el handoff con los bugs encontrados.
Reporta: tabla criterios vs estado + archivos auditados + issues + cobertura.

Cierra con el VERDICT ENVELOPE.
```

---

## Fase 5 — Pruebas manuales y correcciones
> Interactiva. Sesión separada cuando se anticipan más de tres o cuatro bugs.

```text
Correcciones de la US-XXX: [titulo].

Lee, y nada mas:
1. docs/us-handoff/us-XXX.md — COMPLETO
2. docs/manual-test/us-XXX.md
3. git diff --name-only <sha_base> && git diff <sha_base> -- [archivos del handoff]

NO leas los AGENTS.md salvo que el handoff indique que algo se salio del estandar.

Antes de corregir un bug: mem_search "[descripcion del bug]".

- Te reporto bugs uno por uno
- Lee el handoff antes de cambiar algo, para entender por que se hizo asi
- Si la correccion contradice una decision del handoff, explicamelo antes de cambiar
- Si el bug obliga a redesplegar, reporta la revision nueva
- Si obliga a un cambio de schema: NUEVA migracion, jamas editar la aplicada
- Actualiza el handoff con cada bug corregido
- Linters y tests tras cada correccion, solo sobre los archivos tocados

Confirma que leiste el handoff.
```

---

## Fase 6 — QA final post-correcciones
> Solo si en Fase 5 hubo cambios de lógica.

```text
QA final de la US-XXX: [titulo].

Lee la seccion "Bugs resueltos" de docs/us-handoff/us-XXX.md.
git diff --name-only <sha_base> — toda la US, incluidas las correcciones. Solo esos archivos.

1. Linters sin errores
2. Tests sin regresiones
3. Auditoria de seguridad sobre el diff: sin vulnerabilidades nuevas
4. Revision de codigo: no se rompio DRY ni la separacion de capas; sin codigo muerto
5. Las trampas de la Fase 3, una por una, sobre las capas tocadas

mem_save con la observacion final, keywords y patrones que funcionaron.

Actualiza el handoff con estado "ready-to-close".
Reporta: tabla bugs corregidos vs verificados.

Cierra con el VERDICT ENVELOPE. Solo "ok" habilita Fase 7.
```

---

## Fase 7 — Cierre

```text
Cierra la US-XXX: [titulo].

Lee docs/us-handoff/us-XXX.md. Nada mas.

GATE DE ENTRADA: el handoff debe traer un VERDICT ENVELOPE con result "ok".
Si esta "blocked", "warn", o falta: NO cierres. Reporta que falta QA y detente.

1. git status --short
2. Genera docs/us-resolved/us-XXX.md con:
   - Resumen ejecutivo
   - Tabla de criterios de aceptacion: que se hizo + evidencia
   - Cumplimiento de estandares
   - Si desplego: revision de Cloud Run + resultado del smoke test
   - Si migro: nombre de la migracion + confirmacion de schema.sql
   - LLAVE DE PROVENANCE:
     `US-XXX @ <git_sha7> + run:<revision o -> + db:<migracion o ->`
3. Genera el texto del Conventional Commit con scope de epica: feat(E{N}): [descripcion]
4. Actualiza el estado de la US en context/planeacion_proyecto.md
5. Deja la rama lista y ESPERA VISTO BUENO antes de empujar o abrir PR

Puedes borrar docs/us-handoff/us-XXX.md.
```

---

## Ejemplo — las siete pantallas de A4 con fan-out

El caso difícil: mucho trabajo dentro de un solo dominio, con una dependencia real en medio.
**El agente del sistema de diseño va primero y solo**; sin esa secuencia, cuatro agentes pelean
por `main.css` y por el layout.

```text
Programa la US-UX-07: las siete pantallas de alta fidelidad.

Lee docs/us-handoff/us-UX-07.md y la seccion 5 de docs/us-planning/us-UX-07.md.

PASO 1 — SECUENCIAL, un solo agente (frontend-engineer):
  "Sistema de diseno. Lee frontend/AGENTS.md.
   TUS ARCHIVOS: el generador de tokens, frontend/app/assets/css/main.css,
   layouts/default.vue, components/ui/*, pages/guia.vue, pages/index.vue.
   Los tokens se derivan de docs/entregables/estilo/uxdoc.sty. Ningun color a mano.
   La ruta /guia renderiza el sistema vivo; de ahi salen las laminas del documento."

PASO 2 — PARALELO, cuatro agentes frontend-engineer con write-sets disjuntos:

  front/A — ACCESO E INICIO:
  "TUS ARCHIVOS: pages/acceso.vue, pages/inicio.vue, components/home/*.
   NO toques layouts/ ni components/ui/: los importas, no los editas."

  front/B — EXPLORACION Y EXTRACCION:
  "TUS ARCHIVOS: pages/exploracion/*, components/catalog/*, components/charts/*."

  front/C — GOBIERNO DEL DATO:
  "TUS ARCHIVOS: pages/gobierno.vue, components/lineage/*."

  front/D — ADMINISTRACION Y EXPORTACION:
  "TUS ARCHIVOS: pages/administracion.vue, pages/exploracion/exportar.vue, components/admin/*."

PASO 3 — SECUENCIAL, depende del SSE del backend:
  front/E — ASISTENTE:
  "TUS ARCHIVOS: pages/asistente.vue, components/chat/*, composables/useChatStream.ts."

En paralelo al PASO 2, otros dominios que no comparten archivos:
  backend-engineer  -> backend/app/api/*, services/*
  data-engineer     -> ml/data/generators.py, db/migrations/*
  platform-engineer -> Dockerfile, Makefile, despliegue

Integra, luego TESTS en foreground, luego actualiza el handoff.
```

---

## Sesiones recomendadas

| Escenario | Sesión 1 | Sesión 2 |
|-----------|----------|----------|
| US chica, uno o dos dominios | Fases 2-4, **sin repartir** | Fase 5 si hay muchos bugs |
| US grande de un dominio | Fase 2 | Fase 3 con fan-out + Fase 4 |
| US multi-dominio | Fase 2 | Fase 3 con 4+ agentes + Fases 4-5 |
| US de nube | Fase 2 | Fase 3 + Fases 4-7 |
| US de entregable | Fase 2 con la rúbrica delante | Fase 3 con `deliverable-writer` + Fase 4 contra el checklist |
| US ya programada, deuda técnica | Fase 5 | Fases 6-7 |

---

## Mega Prompt — modo desatendido

> Prerequisito: Fase 2 completa. Ejecuta Fases 3, 4 y 6, y se detiene antes de la 7.

Tres reglas absolutas: **no borra nada**, **no empuja a remoto ni abre PR**, y **no cita la salida
de un comando que no corrió**.

```text
Ejecuta la US-XXX: [titulo] de forma autonoma. No me pidas confirmacion para nada. EXCEPCIONES:
- Si ibas a BORRAR un archivo o revertir un commit: NO lo hagas y reportalo al final.
- No empujes a remoto ni abras PR. Deja la rama lista.

PREREQUISITOS:
- docs/us-planning/us-XXX.md debe existir. Si no, detente y reporta.
- docs/us-handoff/us-XXX.md debe existir. Si no, crealo con el template.

FASE 3 — PROGRAMACION:
Lee la seccion 5 de docs/us-planning/us-XXX.md.
git rev-parse HEAD -> escribe el sha7 en "SHA base" del handoff.
Si algun agente genera algo que otros consumen, ese va primero y solo.
Lanza el resto en paralelo con run_in_background, cada uno con SU lista de archivos y su
AGENTS.md de carpeta. Dos agentes NUNCA escriben el mismo archivo.
Respeta las TRAMPAS POR CAPA de la Fase 3 de este documento.

Cuando todos terminen, integra y resuelve conflictos. Luego TESTS en foreground:
  "Lee docs/us-handoff/us-XXX.md. Tests de los archivos nuevos o modificados.
   Mockea SIEMPRE Gemini, GCS y Cloud SQL. Corrige si fallan."

Actualiza el handoff con estado "qa".

FASE 4 — QA en foreground:
  "Lee docs/us-handoff/us-XXX.md. git diff --name-only <sha_base>. Solo esos archivos.
   Linters, tests con cobertura, auditoria de seguridad, revision de codigo, y las skills
   que docs/orchestration/auto-invoke.md indique para las capas tocadas.
   Genera docs/manual-test/us-XXX.md. Actualiza el handoff con bugs y estado 'testing'.
   Cierra con el VERDICT ENVELOPE. Prohibido 'ok' con evidence[] vacio."

FASE 6 — QA FINAL, solo si QA encontro bugs corregibles sin humano:
Corrige linters, tests rojos y desviaciones de las trampas por capa.
Lo que requiera decision humana: documentalo y continua.

AL TERMINAR:
1. Actualiza el handoff con estado "ready-for-human".
2. Reporta:

---
REPORTE US-XXX (Epic E{N}, Actividad A{N})
Dominios/sub-tareas: [front/A, front/B, backend, db, ...]
Fase 3: [OK / ISSUES] — por agente: [archivos] — linter [OK/FAIL] — tests [OK/FAIL XX%]
Fase 4 QA: [N bugs] — Corregidos auto: [lista] — Requieren humano: [lista]
Verdict: [ok / warn / blocked] — evidencia: [3-5 items citables]
Quise borrar (pero no lo hice): [lista o "ninguno"]
Despliegues: [revision o N/A] — Migraciones: [nombre o N/A]
Provenance: US-XXX @ <git_sha7> + run:<revision|-> + db:<migracion|->
Siguiente paso: [Fase 5 con bugs / Fase 7 cierre directo]
---
```

**Reanudación si se interrumpe:**

```text
Reanuda la US-XXX: [titulo].
Lee docs/us-handoff/us-XXX.md PRIMERO — el campo "Estado" dice donde quedamos.
- "starting" o "coding" -> retoma Fase 3; git status dice que ya esta hecho
- "qa"                  -> arranca Fase 4
- "testing"             -> arranca Fase 6
- "ready-for-human"     -> solo reporta el resumen
git checkout [la rama del campo "Rama"]. No repitas trabajo hecho.
```

---

## GitHub Copilot Pro

Copilot lee el `AGENTS.md` del directorio donde edita. No tiene skills, MCP, engram, subagentes ni
navegador: no orquesta fan-out, programa capa por capa. Se compensa pasándole explícitamente el
handoff y el bloque de la US.

Fases 1, 2 y 4 a 7: iguales. La Fase 3 se vuelve secuencial:

```text
Programa la capa [BACKEND|FRONTEND|ML|AGENT|INFRA|DB|DOCS] de la US-XXX: [titulo].
Lee: 1) el AGENTS.md de este directorio  2) docs/us-handoff/us-XXX.md
     3) docs/us-planning/us-XXX.md secs 3, 4, 5
Antes de crear: revisa lo existente aqui para no duplicar.
Respeta las TRAMPAS POR CAPA de docs/orchestration/prompts_optimizers.md.
Todo funcional, cero stubs.
Al terminar: linters y tests de esta capa. Actualiza el handoff.
```
