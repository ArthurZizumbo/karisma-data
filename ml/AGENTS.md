# ml/ — Datos Sintéticos, Capa Semántica y Agente ADK

Guía de carpeta: sobreescribe la raíz dentro de `ml/`. Normas transversales en [`../AGENTS.md`](../AGENTS.md).

## Estructura

```
ml/
├── data/          # generators.py (sintéticos), extractors.py (async + caché TTL), errors.py, seed_catalog.py, embed_catalog.py
├── semantic/      # compiler.py (SMQ: SemanticQuery → Polars lazy), validator.py, joins.py
├── agent/         # ADK: manager → workers; tools/ (buscar_catalogo, consultar_metricas, solicitar_export, resumir_vista)
└── utils/         # DRY compartido de ml/
```

## Reglas — NON-NEGOTIABLE

- Semilla fija SIEMPRE (`SEED = 20260720`) en Polars, Faker y numpy: `make data` es reproducible byte a byte; las 10 consultas de referencia de la capa semántica dependen de ello.
- Esquemas de silos crípticos y heterogéneos A PROPÓSITO (`cli_ref` vs `id_cliente` vs `ctpty_cd`); IDs de cliente compartidos entre silos; ~0.1 % de anomalías inyectadas documentadas en `data/README.md`.
- Capa semántica (SMQ): el LLM y el cliente solo envían `SemanticQuery` validada con Pydantic contra el catálogo; el ÚNICO generador de expresiones Polars es `ml/semantic/compiler.py` (determinístico, lazy, parametrizado). Nunca ejecutar código libre.
- Extractores: `async def` + threadpool (jamás bloquear el event loop), caché TTL configurable, graceful degradation con excepciones tipificadas por silo (`SiloUnavailableError`).
- Tools ADK viven en `ml/agent/tools/`, son funciones Python tipadas que ENVUELVEN endpoints FastAPI gobernados y PROPAGAN el Bearer del usuario — el agente jamás ve datos que el usuario no puede ver. Presupuesto máximo: 5 tool calls.
- Anti-alucinación: toda cifra del agente proviene de un tool call y cita la fuente del catálogo.
- Honestidad de demo: previsiones etiquetadas "proyección simulada"; los datos se declaran sintéticos.
- Jamás llamar a Gemini fuera del agente/embeddings sin span OTel (`llm.call` con `llm.usage.*` y `llm.prompt_hash`; nunca el prompt crudo).

## Comandos

```bash
make data                            # genera data/silos/*.parquet + seed del catálogo (semilla fija)
poetry run pytest tests/ml -q        # extractores, compilador, hit rate
poetry run python -m ml.data.embed_catalog   # job de embeddings Gemini (fase RAG)
make lint                            # ruff + mypy
```

## QA gate específico

- Conectores: pruebas pytest-asyncio de éxito, silo caído y caché hit/miss en verde.
- Compilador: suite de 10 consultas de referencia con resultados esperados sobre la semilla.
- RAG: Hit Rate@3 >= 0.8 sobre el set de 20 consultas antes de cerrar la búsqueda híbrida.
- Agente: cancelación real verificada; evento `tool_call` emitido antes del texto.

## Skills relevantes

| Acción | Skill |
|--------|-------|
| Generadores sintéticos y seeds | `portal-synthetic-data` |
| Extractores async | `portal-data-connectors` |
| Compilador SMQ y joins | `portal-semantic-layer` |
| Búsqueda híbrida y embeddings | `portal-catalog-rag` |
| Tools con Bearer propagado | `portal-auth-jwt` |
