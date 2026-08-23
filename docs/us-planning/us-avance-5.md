# Planning US-AVANCE-5 — Entrega final A5

**Rama**: `us-avance-5` · **SHA base**: `e257131` · **Actividad**: A5, dom 23-ago-2026
**Fuente de verdad del alcance**: [`docs/semana_5/planeacion_excelencia.md`](../semana_5/planeacion_excelencia.md)
**Contrato compartido (cifras, macros, etiquetas, fuentes)**: [`docs/us-handoff/us-avance-5.md`](../us-handoff/us-avance-5.md)

---

## 1. Objetivo

Llevar los 16 criterios de la rúbrica de A5 a banda «Completo». Trece re-evalúan artefactos de
A1–A4 y se cubren cambiando el vehículo de entrega al documento acumulado; los dos nuevos
—métricas UX (15 %) y prueba de usabilidad (20 %)— concentran el trabajo de redacción.

## 2. Criterios de aceptación

1. `Entregable Actividad 5_equipo_8.pdf` compilado desde `main_completo.tex` (Partes I a V) y
   copiado a `docs/semana_5/` con el nombre exacto, sin sufijo de versión.
2. Capítulo de métricas con al menos una métrica por cada una de las siete interfaces de A4,
   citando a Albert y Tullis (2013, caps. 3 a 8).
3. Prueba de usabilidad con la tabla de los 10 pasos de la instrucción, la correspondencia
   tarea a interfaz a funcionalidad principal, y la defensa de n = 5 con fuentes.
4. Las seis retroalimentaciones de A1–A4 cerradas o verificadas, con ADR-005 escrito y los
   espejos de `docs/AGENTS.md` y `docs/CLAUDE.md` sincronizados.
5. URL del demo incluida por variable, con respaldo si el archivo local no existe.
6. Manual de uso del prototipo compilable como Anexo B del acumulado y como PDF propio.
7. Ninguna cifra sin origen; ningún tiempo futuro; ningún dato personal no autorizado.

---

## 3. Write-sets (disjuntos, un dueño por archivo)

| Agente | Sub-tarea | Escribe **solo** | Depende de |
|---|---|---|---|
| **Fase 3** (orquestador) | Contrato generador | `docs/entregables/datos/demo.tex`, `datos/despliegue.tex.example`, `scripts/escribir_url_demo.sh`, `.gitignore`, `docs/entregables/main_a5.tex`, este archivo y el handoff | — |
| **A** | Métricas UX (criterio 14, 15 %) | `docs/entregables/contenido/a5_06_metricas.tex` | contrato |
| **B** | Prueba de usabilidad (criterio 15, 20 %) | `docs/entregables/contenido/a5_04_usabilidad.tex` | contrato |
| **C** | Conclusiones y referencias (criterio 16, 5 %) | `docs/entregables/contenido/a5_05_cierre.tex` | contrato |
| **E** | Maquetación de A3 (retro núm. 2) | `docs/entregables/contenido/a3_01_analisis_competitivo.tex` | ADR-005 |
| **F** | Manual de uso del prototipo | `docs/entregables/contenido/a5_07_manual.tex`, `docs/entregables/main_manual.tex` | contrato |
| **D** | Envoltorio y mapa de cumplimiento | `docs/entregables/main_completo.tex`, `docs/entregables/contenido/a5_00_preliminares.tex` | A, B, C, E, F |
| **Integración** | ADR, guías, compilación, entrega | `docs/decisions/ADR-005-*.md`, `docs/AGENTS.md`, `docs/CLAUDE.md`, `docs/semana_5/*.pdf` | todos |

**Regla de carpeta**: `docs/AGENTS.md` y `docs/CLAUDE.md` son espejos byte-idénticos y los
escribe **un solo autor**: la integración. Ningún agente los toca.

### Archivos prohibidos para todos los agentes

`estilo/uxdoc.sty` · `estilo/a4_tokens.tex` · `estilo/a4_iconos*.tex` · `datos/a4_tokens.json` ·
`contenido/a1_*.tex` · `contenido/a2_*.tex` · `contenido/a3_0[2-6]_*.tex` ·
`contenido/a4_*.tex` · `figuras/**` salvo añadir capturas nuevas bajo `figuras/a5/` ·
cualquier archivo fuera de `docs/`.

---

## 4. Plan de pruebas

Esta US es documental: no añade comportamiento de aplicación. La verificación es de compilación
y de contenido, y solo se escribe una prueba automatizada cuando existe un defecto concreto que
pueda hacerla fallar.

### 4.1 Verificaciones de compilación (obligatorias, las corre cada agente sobre su archivo)

```bash
cd docs/entregables
latexmk -xelatex -interaction=nonstopmode main_completo.tex   # dos pasadas
```

Criterio: cero errores; los avisos de `Overfull \hbox` se revisan pero no bloquean.

### 4.2 Verificaciones de contenido (checklist de la sección 10 del plan)

- Los 16 criterios localizables por su propio título.
- Cada cifra rastreable al contrato C1 o a una cita APA.
- Sin tiempo futuro dentro del entregable, sin emojis, español neutro.
- Sin datos personales más allá de C y V.
- Los ocho mapas de empatía enteros en su página; un competidor por página.

### 4.3 Pruebas automatizadas — solo si hay defecto que las haga fallar

Candidatas evaluadas y su veredicto:

| Prueba candidata | ¿Qué defecto la haría fallar? | Veredicto |
|---|---|---|
| Que `datos/demo.tex` defina `\urlDemoWeb` cuando falta `despliegue.tex` | Que alguien elimine la rama de respaldo del `\IfFileExists` y el repositorio deje de compilar en limpio | **Se escribe si es barata**: comprobación de compilación sin el archivo local |
| Que ningún `.tex` versionado contenga una URL de Cloud Run | Que alguien pegue la dirección literal y publique el identificador del proyecto en un repositorio público | **Se escribe**: es una regresión real de privacidad, del mismo tipo que ya cubre gitleaks |
| Que `a5_06_metricas.tex` mencione las siete interfaces | Que una interfaz se caiga de la tabla al reordenar y el criterio 14 baje de banda | **Se evalúa**: solo si se puede escribir sin fijar la redacción |
| Que el PDF tenga N páginas o que una tabla tenga N filas | Ninguno: fija la maquetación, no el comportamiento | **No se escribe** |
| Cobertura de los `.tex` con vitest o pytest | Ninguno: andamiaje | **No se escribe** |

El agente de tests decide con esta tabla y **no escribe nada** para el que no tenga respuesta.
