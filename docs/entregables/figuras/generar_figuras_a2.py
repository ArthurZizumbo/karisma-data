"""Figures for deliverable A2, built on the same design system as A1.

Produces:
  journey_equipo_laura.png    team journey map, seven stages (landscape)
  journey_diego.png           individual map, Jacqueline
  journey_arturo.png          individual map, Alexandro
  journey_ximena.png          individual map, Arthur
  curva_emocional.png         emotional curve, portal versus current path
  journeys_entrelazados.png   where Laura's journey meets the other personas

Usage:
    python generar_figuras_a2.py <output_dir>
"""

import glob
import sys
import textwrap
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

warnings.filterwarnings("ignore")

# TrueType fonts in the PDF output: avoids Type 3 subsets whose glyphs render
# incorrectly in some viewers.
matplotlib.rcParams["pdf.fonttype"] = 42
matplotlib.rcParams["ps.fonttype"] = 42

OUT = (sys.argv[1] if len(sys.argv) > 1 else ".").rstrip("\\/")

# --- Design system ---------------------------------------------------------
NAVY = "#1F4D78"
BLUE = "#2563EB"
SKY = "#3B82F6"
PALE = "#B8CCE4"
AMBER = "#F97316"
SURFACE = "#F8FAFC"
INK = "#1E293B"
MUTED = "#64748B"
LINE = "#CBD5E1"
RED = "#B91C1C"
GREEN = "#166534"
OPP = "#FFF7ED"
OPP_EDGE = "#FED7AA"

for pattern in (
    r"C:\Users\*\AppData\Local\Programs\MiKTeX\fonts\**\fira\*.otf",
    r"C:\Users\*\AppData\Local\Programs\MiKTeX\fonts\**\lexend*\*.ttf",
    r"C:\Program Files\MiKTeX\fonts\**\fira\*.otf",
    r"C:\Program Files\MiKTeX\fonts\**\lexend*\*.ttf",
):
    for path in glob.glob(pattern, recursive=True):
        try:
            font_manager.fontManager.addfont(path)
        except Exception:
            pass

FAMILIES = {f.name for f in font_manager.fontManager.ttflist}
BODY = "Fira Sans" if "Fira Sans" in FAMILIES else "DejaVu Sans"
HEAD = "Lexend" if "Lexend" in FAMILIES else BODY
print(f"tipografia -> titulos: {HEAD} | cuerpo: {BODY}")

sns.set_theme(
    style="white",
    rc={
        "font.family": BODY,
        "font.size": 9,
        "text.color": INK,
        "axes.labelcolor": NAVY,
        "axes.edgecolor": LINE,
        "xtick.color": MUTED,
        "ytick.color": MUTED,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
    },
)

from journey_data import AFTER, ARTURO, BEFORE, DIEGO, DURING, LAURA, MAPS, XIMENA  # noqa: F401

PHASE_COLORS = {BEFORE: PALE, DURING: SKY, AFTER: PALE}



def rounded(ax, x, y, w, h, face, edge=None, lw=0.8, radius=0.02, z=1, ls="solid"):
    """Draw a rounded rectangle in axes coordinates."""
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=face, edgecolor=edge if edge else face,
        linewidth=lw, linestyle=ls, zorder=z,
    )
    ax.add_patch(box)
    return box


def journey_map(path, spec):
    """Full journey map: phase band, stage band and five content lanes."""
    stages = spec["stages"]
    n = len(stages)
    fig, ax = plt.subplots(figsize=(16.5, 9.7))
    ax.set_xlim(0, 1)
    ax.set_ylim(-0.06, 1.03)
    ax.axis("off")

    label_w = 0.088
    gap = 0.004
    col_w = (1 - label_w - gap * (n + 1)) / n

    def col_x(i):
        return label_w + gap * (i + 1) + col_w * i

    lanes = [
        ("Acciones", "actions", 0.128),
        ("Puntos de contacto", "touchpoints", 0.095),
        ("Pensamientos", "thoughts", 0.100),
        ("Emociones", None, 0.150),
        ("Puntos de fricción", "pain", 0.128),
        ("Oportunidades", "opportunity", 0.128),
    ]

    top = 0.945
    phase_h = 0.034
    stage_h = 0.046

    ax.text(0, 1.005, spec["title"], fontsize=21, color=NAVY, family=HEAD, va="top")
    ax.text(0, 0.950, spec["subtitle"], fontsize=12, color=MUTED, va="top")

    y = top - 0.045

    # Phase band: merge consecutive stages that share a phase
    start = 0
    for i in range(n + 1):
        if i == n or stages[i]["phase"] != stages[start]["phase"]:
            phase = stages[start]["phase"]
            x0, x1 = col_x(start), col_x(i - 1) + col_w
            rounded(ax, x0, y - phase_h, x1 - x0, phase_h, PHASE_COLORS[phase],
                    radius=0.012)
            ax.text((x0 + x1) / 2, y - phase_h / 2, phase.upper(), ha="center",
                    va="center", fontsize=11, family=HEAD,
                    color="white" if phase == DURING else NAVY)
            start = i
    ax.text(label_w - 0.006, y - phase_h / 2, "MOMENTO", ha="right", va="center",
            fontsize=10.5, color=MUTED, family=HEAD)

    y -= phase_h + gap

    for i, stage in enumerate(stages):
        rounded(ax, col_x(i), y - stage_h, col_w, stage_h, NAVY, radius=0.012)
        ax.text(col_x(i) + col_w / 2, y - stage_h / 2, stage["name"], ha="center",
                va="center", fontsize=14, color="white", family=HEAD)
    ax.text(label_w - 0.006, y - stage_h / 2, "ETAPAS", ha="right", va="center",
            fontsize=10.5, color=NAVY, family=HEAD)

    y -= stage_h + gap * 2
    y_stage_bottom = y + gap * 2

    for lane_name, key, lane_h in lanes:
        ax.text(label_w - 0.006, y - lane_h / 2, lane_name.upper(), ha="right",
                va="center", fontsize=10.5, color=NAVY, family=HEAD)
        if key is None:
            emotion_lane(ax, y, lane_h, col_x, col_w, stages)
        else:
            face = OPP if lane_name == "Oportunidades" else SURFACE
            edge = OPP_EDGE if lane_name == "Oportunidades" else LINE
            for i, stage in enumerate(stages):
                rounded(ax, col_x(i), y - lane_h, col_w, lane_h, face, edge,
                        lw=0.8, radius=0.010)
                ax.text(col_x(i) + col_w / 2, y - lane_h / 2, stage[key],
                        ha="center", va="center", fontsize=10.5, color=INK,
                        linespacing=1.45)
        y -= lane_h + gap

    # Moment of truth: frame the whole column and label it below
    t = spec["truth"]
    mt_x = col_x(t) + col_w / 2
    rounded(ax, col_x(t) - 0.005, y + gap - 0.004, col_w + 0.010,
            y_stage_bottom - y - gap + 0.008, "none", AMBER, lw=1.6,
            radius=0.012, z=6, ls=(0, (5, 3)))
    ax.text(mt_x, y - 0.010, "MOMENTO DE LA VERDAD", ha="center", va="top",
            fontsize=11, color=AMBER, family=HEAD)

    ax.text(0, -0.050,
            "Escala emocional declarada: -2 bloqueo (la tarea deja de depender del usuario) · "
            "0 neutro · +2 confianza (puede responder por su trabajo)." + chr(10) +
            "Pensamientos y emociones provienen de los cuadrantes Thinks y Feels del mapa de "
            "empatía de la Actividad 1.",
            fontsize=9.5, color=MUTED, va="bottom")

    for ext in ("pdf", "png"):
        fig.savefig(f"{path}.{ext}", dpi=220, bbox_inches="tight",
                    facecolor="white", pad_inches=0.25)
    plt.close(fig)
    print(f"escrito {path}.pdf / .png")


def emotion_lane(ax, y_top, lane_h, col_x, col_w, stages):
    """Emotion lane: dotted grid, curve and coloured markers."""
    n = len(stages)
    x0, x1 = col_x(0), col_x(n - 1) + col_w
    rounded(ax, x0, y_top - lane_h, x1 - x0, lane_h, "white", LINE, lw=0.8,
            radius=0.010)

    def y_for(value):
        margin = 0.018
        low, high = y_top - lane_h + margin, y_top - margin
        return low + (value + 2) / 4 * (high - low)

    for value in (-2, -1, 0, 1, 2):
        style = "-" if value == 0 else ":"
        ax.plot([x0 + 0.004, x1 - 0.004], [y_for(value)] * 2, style,
                color=LINE if value else PALE, lw=0.8, zorder=1)
        ax.text(x0 + 0.006, y_for(value), f"{value:+d}" if value else " 0",
                fontsize=9, color=MUTED, va="center", ha="left", zorder=3)

    xs = [col_x(i) + col_w / 2 for i in range(n)]
    ys = [y_for(stage["emotion"]) for stage in stages]
    ax.plot(xs, ys, "-", color=BLUE, lw=2.2, zorder=4)

    for x, stage in zip(xs, stages):
        value = stage["emotion"]
        color = GREEN if value > 0 else (RED if value < 0 else MUTED)
        ax.plot([x], [y_for(value)], "o", color=color, markersize=11,
                markeredgecolor="white", markeredgewidth=1.6, zorder=5)


def emotional_curve(path):
    """Comparison between the portal path and the current path, for Laura."""
    labels = [s["name"] for s in LAURA["stages"]]
    with_portal = [s["emotion"] for s in LAURA["stages"]]
    without_portal = [-1, -1, -1, -2, -1, 0, -2]

    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    ax.axhline(0, color=LINE, lw=1)
    for value in (-2, -1, 1, 2):
        ax.axhline(value, color=LINE, lw=0.6, ls=":")

    x = list(range(len(labels)))
    ax.plot(x, with_portal, "-o", color=BLUE, lw=2.6, markersize=9,
            markeredgecolor="white", markeredgewidth=1.6,
            label="Recorrido con Karisma Data", zorder=4)
    ax.plot(x, without_portal, "--o", color=MUTED, lw=1.8, markersize=7,
            markerfacecolor="white", label="Recorrido actual sin portal", zorder=3)
    ax.fill_between(x, without_portal, with_portal, color=SKY, alpha=0.10, zorder=1)

    ax.annotate("Momento de la verdad:\nla ficha del catálogo responde\nsin intermediarios",
                xy=(3, 2), xytext=(1.35, 1.55), fontsize=8.4, color=NAVY,
                ha="left", va="center",
                arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=1.1,
                                connectionstyle="arc3,rad=-0.15"))
    ax.annotate("Hoy aquí la tarea se detiene:\ndepende de que un colega conteste",
                xy=(3, -2), xytext=(0.15, -2.25), fontsize=8.4, color=RED,
                ha="left", va="center",
                arrowprops=dict(arrowstyle="-|>", color=RED, lw=1.1,
                                connectionstyle="arc3,rad=0.15"))

    ax.set_xticks(x)
    ax.set_xticklabels([textwrap.fill(label, 18) for label in labels], fontsize=8.6,
                       color=NAVY)
    ax.set_yticks([-2, -1, 0, 1, 2])
    ax.set_yticklabels(["-2 bloqueo", "-1", "0 neutro", "+1", "+2 confianza"],
                       fontsize=8.6, color=MUTED)
    ax.set_ylim(-2.75, 2.75)
    ax.set_xlim(-0.4, len(labels) - 0.6)

    for spine in ("top", "right", "left", "bottom"):
        ax.spines[spine].set_visible(spine == "bottom")
    ax.spines["bottom"].set_color(LINE)
    ax.grid(False)
    ax.tick_params(length=0)
    ax.legend(loc="upper left", frameon=False, fontsize=8.6, ncol=1,
              bbox_to_anchor=(-0.02, 1.06))

    fig.tight_layout()
    for ext in ("pdf", "png"):
        fig.savefig(f"{path}.{ext}", dpi=220, facecolor="white",
                    bbox_inches="tight", pad_inches=0.18)
    plt.close(fig)
    print(f"escrito {path}.pdf / .png")


def interlocked_journeys(path):
    """Laura's journey as the spine, with the points where other personas meet it."""
    stages = LAURA["stages"]
    fig, ax = plt.subplots(figsize=(11.0, 5.4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    n = len(stages)
    x_start, x_end = 0.105, 0.900
    step = (x_end - x_start) / (n - 1)
    xs = [x_start + step * i for i in range(n)]
    y_spine = 0.50

    ax.plot([x_start - 0.02, x_end + 0.02], [y_spine] * 2, "-", color=PALE, lw=7,
            solid_capstyle="round", zorder=1)

    for x, stage in zip(xs, stages):
        ax.plot([x], [y_spine], "o", color=NAVY, markersize=15,
                markeredgecolor="white", markeredgewidth=2, zorder=4)
        ax.text(x, y_spine, stage["name"].split(".")[0], ha="center", va="center",
                fontsize=8.5, color="white", family=HEAD, zorder=5)
        ax.text(x, y_spine - 0.055, stage["name"].split(". ")[1], ha="center",
                va="top", fontsize=8.2, color=NAVY, family=HEAD)

    ax.text(0.5, 0.955, "Recorrido de Laura Méndez y sus puntos de encuentro",
            ha="center", fontsize=13, color=NAVY, family=HEAD)

    # (stage index, persona, relation, above?, horizontal offset of the card)
    links = [
        (1, "Mariana Ovalle", "da de alta la cuenta\ncon el rol correcto", True, 0.0),
        (3, "Roberto Valdez", "publica la definición\nque Laura valida", True, 0.0),
        (6, "Roberto Valdez", "emite el aviso de\ncambio de versión", True, 0.0),
        (2, "Diego Hernández", "explora las fuentes\nrelacionadas a diario", False, -0.105),
        (5, "Arturo Castañeda", "consume el indicador\nque esa cifra alimenta", False, 0.105),
    ]

    for idx, persona, relation, above, dx in links:
        x = xs[idx]
        xc = x + dx
        y_box = 0.79 if above else 0.175
        w, h = 0.185, 0.135
        rounded(ax, xc - w / 2, y_box - h / 2, w, h, SURFACE, LINE, lw=0.9,
                radius=0.02, z=3)
        ax.text(xc, y_box + 0.032, persona, ha="center", va="center", fontsize=8.8,
                color=NAVY, family=HEAD, zorder=4)
        ax.text(xc, y_box - 0.022, relation, ha="center", va="center", fontsize=7.9,
                color=INK, linespacing=1.4, zorder=4)

        y_from = y_box - h / 2 if above else y_box + h / 2
        y_to = y_spine + 0.035 if above else y_spine - 0.030
        rad = 0.0 if above else (0.25 if dx < 0 else -0.25)
        ax.add_patch(FancyArrowPatch((xc, y_from), (x, y_to),
                                     arrowstyle="-|>", mutation_scale=11,
                                     color=AMBER if above else SKY, lw=1.4,
                                     connectionstyle=f"arc3,rad={rad}", zorder=2))

    ax.text(0.5, 0.035,
            "Arriba, las tareas de las que depende el recorrido de Laura. "
            "Abajo, los recorridos que se alimentan de él.",
            ha="center", fontsize=8.4, color=MUTED)

    for ext in ("pdf", "png"):
        fig.savefig(f"{path}.{ext}", dpi=220, facecolor="white",
                    bbox_inches="tight", pad_inches=0.2)
    plt.close(fig)
    print(f"escrito {path}.pdf / .png")


if __name__ == "__main__":
    # Los cuatro journey maps se componen con HTML y CSS Grid
    # (journey_html/render.py): una retícula de etapas por carriles es un
    # problema de maquetación, no de graficación. Aquí quedan las dos figuras
    # que sí son gráficas de datos.
    emotional_curve(f"{OUT}/curva_emocional")
    interlocked_journeys(f"{OUT}/journeys_entrelazados")
