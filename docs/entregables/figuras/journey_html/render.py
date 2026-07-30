"""Render the four journey maps as print-ready PDFs from HTML and CSS Grid.

Reads the shared content module (``journey_data``) and produces one self
contained HTML file per map, then prints each one to PDF with headless Edge.
No extra dependencies: Edge ships with Windows and the fonts come from the
local MiKTeX installation, the same ones the LaTeX document uses.

Usage:
    python render.py [output_dir]        # defaults to the figuras/ folder
"""

import base64
import glob
import html
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from journey_data import AFTER, BEFORE, DURING, MAPS  # noqa: E402

OUT = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else HERE.parent
BUILD = HERE / "build"

EDGE_CANDIDATES = [
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
]

FONT_PATTERNS = {
    "FUENTE_LEXEND": [
        r"C:\Users\*\AppData\Local\Programs\MiKTeX\fonts\**\LexendDeca-Regular.ttf",
        r"C:\Program Files\MiKTeX\fonts\**\LexendDeca-Regular.ttf",
    ],
    "FUENTE_FIRA_REGULAR": [
        r"C:\Users\*\AppData\Local\Programs\MiKTeX\fonts\**\FiraSans-Regular.otf",
        r"C:\Program Files\MiKTeX\fonts\**\FiraSans-Regular.otf",
    ],
    "FUENTE_FIRA_MEDIUM": [
        r"C:\Users\*\AppData\Local\Programs\MiKTeX\fonts\**\FiraSans-Medium.otf",
        r"C:\Program Files\MiKTeX\fonts\**\FiraSans-Medium.otf",
    ],
    "FUENTE_FIRA_SEMIBOLD": [
        r"C:\Users\*\AppData\Local\Programs\MiKTeX\fonts\**\FiraSans-SemiBold.otf",
        r"C:\Program Files\MiKTeX\fonts\**\FiraSans-SemiBold.otf",
    ],
}

# Geometry of the emotion lane, in percentages of its own height.
LANE_TOP, LANE_BOTTOM = 26.0, 80.0


def find_font(patterns):
    """Return the font as a data URI so the page works from any origin."""
    for pattern in patterns:
        matches = glob.glob(pattern, recursive=True)
        if matches:
            path = Path(matches[0])
            mime = "font/otf" if path.suffix == ".otf" else "font/ttf"
            blob = base64.b64encode(path.read_bytes()).decode("ascii")
            return f"data:{mime};base64,{blob}"
    raise SystemExit(f"no se encontro ninguna fuente para {patterns[0]}")


def css():
    text = (HERE / "estilo.css").read_text(encoding="utf-8")
    for token, patterns in FONT_PATTERNS.items():
        text = text.replace(token, find_font(patterns))
    return text


def y_for(value):
    """Vertical position, in percent, of an emotion value on the lane."""
    return LANE_BOTTOM - (value + 2) / 4 * (LANE_BOTTOM - LANE_TOP)


def phase_class(phase):
    return {BEFORE: "previo", DURING: "durante", AFTER: "posterior"}[phase]


def cell(text, col, extra=""):
    """Content cell. The column is explicit so the highlight never shifts it."""
    body = html.escape(text).replace("\n", "<br>")
    return f'<div class="celda {extra}" style="grid-column: {col}">{body}</div>'


def cells(stages, key, extra=""):
    return "".join(cell(s[key], i + 2, extra) for i, s in enumerate(stages))


def lane_label(group, title, extra=""):
    """Build a Custellence-style lane label with perspective and lane name."""
    return (
        f'<div class="etiqueta {extra}">'
        f'<span class="grupo">{html.escape(group)}</span>'
        f'<span>{html.escape(title)}</span></div>'
    )


def phase_band(stages):
    """Merge consecutive stages that share a phase into a single pill."""
    out, start = [], 0
    for i in range(len(stages) + 1):
        if i == len(stages) or stages[i]["phase"] != stages[start]["phase"]:
            phase = stages[start]["phase"]
            out.append(
                f'<div class="fase {phase_class(phase)}" '
                f'style="grid-column: {start + 2} / {i + 2}">'
                f'{html.escape(phase)}</div>'
            )
            start = i
    return "".join(out)


def stage_band(stages):
    out = []
    for i, stage in enumerate(stages):
        num, _, name = stage["name"].partition(". ")
        out.append(
            f'<div class="etapa" style="grid-column: {i + 2}">'
            f'<span class="num">Etapa {num}</span>{html.escape(name)}</div>'
        )
    return "".join(out)


def emotion_lane(stages):
    n = len(stages)
    guides = []
    for value in (2, 1, 0, -1, -2):
        label = f"{value:+d}" if value else "0"
        guides.append(
            f'<div class="guia{" cero" if value == 0 else ""}" '
            f'style="top: {y_for(value):.2f}%"><span>{label}</span></div>'
        )

    points, marks = [], []
    for i, stage in enumerate(stages):
        value = stage["emotion"]
        x = (i + 0.5) / n * 100
        y = y_for(value)
        points.append(f"{x:.3f},{y:.3f}")
        shape = "alza" if value > 0 else ("baja" if value < 0 else "neutro")
        # El rótulo se coloca del lado opuesto a la curva para no cruzarla.
        offset = "12px" if value < 0 else "-25px"
        label = f"{value:+d}" if value else "0"
        marks.append(
            f'<div class="punto">'
            f'<div class="marca {shape}" style="top: {y:.2f}%"></div>'
            f'<div class="valor" style="top: calc({y:.2f}% + {offset})">{label}</div>'
            f"</div>"
        )

    polyline = (
        f'<svg class="trazo" viewBox="0 0 100 100" preserveAspectRatio="none">'
        f'<polyline points="{" ".join(points)}" fill="none" stroke="#5568D9" '
        f'stroke-width="3.2" vector-effect="non-scaling-stroke" '
        f'stroke-linejoin="round" stroke-linecap="round"/></svg>'
    )

    return (
        '<div class="emociones">'
        f'<div class="guias">{"".join(guides)}</div>'
        f"{polyline}"
        f'<div class="puntos">{"".join(marks)}</div>'
        "</div>"
    )


def build_html(spec):
    stages = spec["stages"]
    n = len(stages)
    title, _, subject = spec["title"].partition(" · ")
    goal, _, rest = spec["subtitle"].partition("   ·   ")
    tags = [t.strip() for t in rest.split("   ·   ") if t.strip()]

    rows = [
        (lane_label("Estructura", "Momento", "tenue estructura"), phase_band(stages),
         "fila-momento"),
        (lane_label("Estructura", "Etapas", "estructura"), stage_band(stages), "fila-etapa"),
        (lane_label("Usuario", "Acciones", "usuario"),
         cells(stages, "actions"), "fila-accion"),
        (lane_label("Interacción", "Puntos de contacto", "interaccion"),
         cells(stages, "touchpoints", "contacto"), "fila-contacto"),
        (lane_label("Experiencia", "Pensamientos", "experiencia"),
         cells(stages, "thoughts", "pensamiento"), "fila-pensamiento"),
        (lane_label("Experiencia", "Emociones", "experiencia"), emotion_lane(stages),
         "fila-emocion"),
        (lane_label("Análisis", "Puntos de fricción", "analisis"),
         cells(stages, "pain"), "fila-friccion"),
        (lane_label("Desarrollo", "Oportunidades", "desarrollo"),
         cells(stages, "opportunity", "oportunidad"), "fila-oportunidad"),
    ]

    grid = "".join(
        f'<div class="fila {css_class}" style="display: contents">{label}{cells}</div>'
        for label, cells, css_class in rows
    )

    # Realce del momento de la verdad: una celda de la retícula que ocupa la
    # columna de la etapa, desde la banda de etapas hasta el último carril.
    t = spec["truth"]
    frame = (
        f'<div class="destacado" style="grid-column: {t + 2}">'
        f'<span class="rotulo-verdad">Momento de la verdad</span></div>'
    )

    return f"""<!doctype html>
<html lang="es"><head><meta charset="utf-8">
<title>{html.escape(spec['title'])}</title>
<style>{css()}</style>
</head><body style="--n: {n}">
  <header class="cabecera">
    <div>
      <h1>{html.escape(title)} · {html.escape(subject)}</h1>
      <p class="objetivo"><strong>{html.escape(goal)}</strong></p>
    </div>
    <div class="sello">
      <span class="nombre">Karisma Data</span>
      {"".join(f'<span class="chip">{html.escape(t)}</span>' for t in tags)}
    </div>
  </header>

  <main class="mapa{' denso' if n >= 7 else ''}">
    {grid}
    {frame}
  </main>

  <footer class="pie">
    <div class="leyenda">
      <span class="item"><span class="muestra alza"></span>Confianza (+1, +2)</span>
      <span class="item"><span class="muestra neutro"></span>Neutro (0)</span>
      <span class="item"><span class="muestra baja"></span>Fricción (-1, -2)</span>
    </div>
    <div>
      Escala emocional declarada: -2 bloqueo, la tarea deja de depender del usuario ·
      0 neutro · +2 confianza, puede responder por su trabajo.<br>
      Pensamientos y emociones proceden de los cuadrantes Thinks y Feels del mapa de
      empatía de la Actividad 1.
    </div>
  </footer>
</body></html>
"""


def edge():
    for path in EDGE_CANDIDATES:
        if Path(path).exists():
            return path
    raise SystemExit("no se encontro msedge.exe")


def main():
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(parents=True, exist_ok=True)
    browser = edge()

    for name, spec in MAPS:
        page = BUILD / f"{name}.html"
        page.write_text(build_html(spec), encoding="utf-8")
        pdf = OUT / f"{name}.pdf"
        subprocess.run(
            [browser, "--headless=new", "--disable-gpu", "--no-sandbox",
             "--no-pdf-header-footer", f"--print-to-pdf={pdf}", page.as_uri()],
            check=True, capture_output=True, timeout=120,
        )
        print(f"escrito {pdf.name}  <-  {page.name}")


if __name__ == "__main__":
    main()
