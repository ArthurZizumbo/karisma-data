"""Figuras del entregable A1, construidas con seaborn sobre el sistema de diseno del documento.

Paleta y tipografia provienen del design system: Lexend / Fira Sans, azul corporativo con
acento ambar verificado para contraste WCAG.
"""

import glob
import sys
import warnings

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib import font_manager
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

warnings.filterwarnings("ignore")

OUT = sys.argv[1].rstrip("\\/")

# --- Sistema de diseno -----------------------------------------------------
NAVY = "#1F4D78"
BLUE = "#2563EB"
SKY = "#3B82F6"
PALE = "#B8CCE4"
AMBER = "#F97316"
SURFACE = "#F8FAFC"
INK = "#1E293B"
MUTED = "#64748B"
LINE = "#CBD5E1"

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
    style="whitegrid",
    rc={
        "font.family": BODY,
        "font.size": 9.5,
        "axes.labelcolor": NAVY,
        "axes.edgecolor": LINE,
        "axes.titlecolor": NAVY,
        "text.color": INK,
        "xtick.color": INK,
        "ytick.color": INK,
        "grid.color": "#E2E8F0",
        "grid.linewidth": 0.7,
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "savefig.facecolor": "white",
    },
)

PERFILES = [
    "Operativo",
    "Analista de datos",
    "Propietario de datos",
    "Riesgos y auditoría",
    "Ingeniería de datos",
    "Directivo",
    "Administración de plataforma",
    "Integración de aplicaciones",
]


# ------------------------------------------------------- Figura 1: audiencia
def figura_1():
    datos = pd.DataFrame(
        {
            "perfil": PERFILES,
            "profundidad": [1.6, 6.4, 4.4, 6.0, 8.9, 1.2, 7.6, 8.6],
            "responsabilidad": [1.5, 2.4, 8.4, 7.4, 5.4, 6.2, 8.9, 2.0],
            "relacion": [
                "Consume el dato",
                "Consume el dato",
                "Gobierna el dato",
                "Gobierna el dato",
                "Habilita el dato",
                "Consume el dato",
                "Gobierna el dato",
                "Habilita el dato",
            ],
        }
    )

    fig, ax = plt.subplots(figsize=(9.6, 6.2))
    ax.axvspan(0, 5.3, color=SURFACE, zorder=0)
    ax.axhspan(5.3, 10.6, color="#EEF3FA", alpha=0.55, zorder=0)

    sns.scatterplot(
        data=datos, x="profundidad", y="responsabilidad", hue="relacion",
        palette={"Consume el dato": PALE, "Habilita el dato": SKY, "Gobierna el dato": NAVY},
        s=460, edgecolor="white", linewidth=2.2, ax=ax, zorder=4,
        hue_order=["Consume el dato", "Habilita el dato", "Gobierna el dato"],
    )

    for _, fila in datos.iterrows():
        ax.annotate(
            fila["perfil"], (fila["profundidad"], fila["responsabilidad"]),
            xytext=(0, -27), textcoords="offset points", ha="center",
            fontsize=9, color=INK, zorder=6,
        )

    ax.axvline(5.3, color=LINE, lw=1, zorder=1)
    ax.axhline(5.3, color=LINE, lw=1, zorder=1)
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0, 10.6)
    ax.set_xlabel("Profundidad técnica  →", fontsize=10.5, fontweight="bold", labelpad=10)
    ax.set_ylabel("Responsabilidad sobre el dato  →", fontsize=10.5, fontweight="bold", labelpad=10)
    ax.set_xticks([1.3, 8.9])
    ax.set_xticklabels(["Consulta en buscador", "SQL, APIs y modelado"], fontsize=9)
    ax.set_yticks([1.3, 8.9])
    ax.set_yticklabels(["Consume", "Gobierna\ny controla"], fontsize=9)
    ax.grid(False)
    sns.despine(ax=ax, top=True, right=True)
    ax.legend(title="", loc="lower center", bbox_to_anchor=(0.5, -0.22),
              ncol=3, frameon=False, fontsize=9.5)

    fig.tight_layout()
    fig.savefig(f"{OUT}/fig1_mapa_audiencia.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------- Figura 2: impacto
def figura_2():
    columnas = ["Tiempo de\nrespuesta", "Retrabajo", "Riesgo de\ninterpretación",
                "Evidencia y\ntrazabilidad", "Calidad de\nla decisión"]
    valores = np.array([
        [3, 3, 3, 1, 2],
        [3, 3, 3, 2, 2],
        [2, 3, 3, 3, 2],
        [2, 2, 2, 3, 2],
        [2, 3, 1, 2, 1],
        [1, 1, 3, 2, 3],
        [1, 2, 1, 3, 1],
        [2, 3, 3, 2, 1],
    ])
    etiquetas = np.vectorize({3: "Alto", 2: "Medio", 1: "Bajo"}.get)(valores)
    datos = pd.DataFrame(valores, index=PERFILES, columns=columnas)

    fig, ax = plt.subplots(figsize=(9.8, 5.8))
    sns.heatmap(
        datos, annot=etiquetas, fmt="", cmap=sns.color_palette([PALE, SKY, NAVY], as_cmap=True),
        vmin=1, vmax=3, linewidths=2.4, linecolor="white", cbar=False, ax=ax,
        annot_kws={"fontsize": 9, "fontweight": "bold"},
    )
    for texto, valor in zip(ax.texts, valores.flatten()):
        texto.set_color("white" if valor >= 2 else INK)

    ax.set_xticklabels(ax.get_xticklabels(), rotation=0, fontsize=9.5,
                       fontweight="bold", color=NAVY)
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=9.5)
    ax.xaxis.tick_top()
    ax.tick_params(length=0)
    ax.set_xlabel("")
    ax.set_ylabel("")

    leyenda = [
        mpatches.Patch(facecolor=NAVY, label="Alto"),
        mpatches.Patch(facecolor=SKY, label="Medio"),
        mpatches.Patch(facecolor=PALE, label="Bajo"),
    ]
    ax.legend(handles=leyenda, loc="upper center", bbox_to_anchor=(0.5, -0.06),
              ncol=3, frameon=False, fontsize=9.5, title="Intensidad del impacto",
              title_fontsize=9.5)

    fig.tight_layout()
    fig.savefig(f"{OUT}/fig2_impacto_por_perfil.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------- Figura 3: flujos
def caja(ax, x, y, w, h, texto, fc, ec=LINE, tc=INK, fs=8.5, bold=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.06",
                                linewidth=1.1, edgecolor=ec, facecolor=fc))
    ax.text(x + w / 2, y + h / 2, texto, ha="center", va="center", fontsize=fs,
            color=tc, fontweight="bold" if bold else "normal", zorder=5,
            fontfamily=BODY)


def flecha(ax, p1, p2, color=SKY, lw=1.2, rad=0.0):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=11,
                                 linewidth=lw, color=color,
                                 connectionstyle=f"arc3,rad={rad}", shrinkA=2, shrinkB=3))


def figura_3():
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(11.6, 5.1))
    for ax in (a1, a2):
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")
        ax.grid(False)

    a1.text(5, 9.6, "Flujo actual", ha="center", fontsize=13, fontweight="bold",
            color=NAVY, fontfamily=HEAD)
    a1.text(5, 9.0, "una persona, muchas puertas", ha="center", fontsize=9,
            color=MUTED, style="italic")
    caja(a1, 0.2, 4.3, 2.0, 1.3, "Persona\nusuaria", SURFACE, bold=True)

    fuentes = [("Base de\ncréditos", 7.6), ("Base de\nliquidez", 6.1),
               ("Base de\nderivados", 4.6), ("Carpeta\ncompartida", 3.1),
               ("Correo del\nárea", 1.6), ("Colega que\n\"sí sabe\"", 0.1)]
    for i, (etiqueta, y) in enumerate(fuentes):
        caja(a1, 6.4, y, 3.3, 1.15, etiqueta, PALE if i % 2 else "#E7EEF7")
        flecha(a1, (2.25, 4.95), (6.35, y + 0.58), color="#94A3B8",
               rad=0.18 if y > 4.9 else -0.18)

    a1.text(4.3, 8.2, "accesos distintos", ha="center", fontsize=8, color=AMBER,
            style="italic", fontweight="bold")
    a1.text(4.3, 2.0, "definiciones dispersas", ha="center", fontsize=8, color=AMBER,
            style="italic", fontweight="bold")
    a1.text(5, -0.4, "Repetir el recorrido si la fuente no era la correcta",
            ha="center", fontsize=8.5, color=AMBER, fontweight="bold")

    a2.text(5, 9.6, "Flujo propuesto", ha="center", fontsize=13, fontweight="bold",
            color=NAVY, fontfamily=HEAD)
    a2.text(5, 9.0, "una capa que federa las mismas fuentes", ha="center", fontsize=9,
            color=MUTED, style="italic")
    caja(a2, 0.2, 4.3, 2.0, 1.3, "Persona\nusuaria", SURFACE, bold=True)
    flecha(a2, (2.25, 4.95), (3.35, 4.95), color=BLUE, lw=1.9)

    caja(a2, 3.4, 3.05, 6.3, 3.9, "", "white", ec=NAVY)
    a2.text(6.55, 6.45, "Karisma Data", ha="center", fontsize=10.5,
            fontweight="bold", color=NAVY, fontfamily=HEAD)
    for i, (modulo, nota) in enumerate([
        ("Buscador unificado", "por concepto, no por sistema"),
        ("Catálogo semántico", "definición, dueño y vigencia"),
        ("Trazabilidad", "origen y fecha de cada cifra"),
        ("Exportación y API", "sin bloquear la pantalla"),
    ]):
        y = 5.75 - i * 0.72
        a2.text(3.75, y, "\u25cf", fontsize=7, color=BLUE, va="center")
        a2.text(4.05, y, modulo, fontsize=9, color=INK, va="center", fontweight="bold")
        a2.text(6.45, y, nota, fontsize=8, color=MUTED, va="center", style="italic")

    for i, etiqueta in enumerate(["Créditos", "Liquidez", "Derivados"]):
        x = 3.4 + i * 2.15
        caja(a2, x, 1.1, 2.0, 1.0, etiqueta, "#E7EEF7")
        flecha(a2, (x + 1.0, 3.0), (x + 1.0, 2.15), color="#94A3B8", lw=1.0)

    a2.text(5, -0.4, "Un solo recorrido, con la fuente y la fecha a la vista",
            ha="center", fontsize=8.5, color="#166534", fontweight="bold")

    fig.tight_layout()
    fig.savefig(f"{OUT}/fig3_flujo_actual_propuesto.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


# -------------------------------------------------------- Figura 4: concepto
def figura_4():
    fig, ax = plt.subplots(figsize=(9.8, 7.0))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.4)
    ax.axis("off")
    ax.grid(False)

    caja(ax, 0.1, 0.1, 9.8, 7.2, "", "white", ec=LINE)
    ax.add_patch(mpatches.Rectangle((0.1, 6.55), 9.8, 0.75, facecolor=NAVY, edgecolor=NAVY))
    ax.text(0.45, 6.93, "Karisma Data", fontsize=10.5, color="white",
            fontweight="bold", va="center", fontfamily=HEAD)
    ax.text(9.55, 6.93, "Perfil: Operativo", fontsize=8.5, color="#CBD5E1",
            va="center", ha="right")

    caja(ax, 0.45, 5.72, 7.4, 0.62, "", "white", ec="#94A3B8")
    ax.text(0.72, 6.03, "mora por producto", fontsize=10, color=INK, va="center")
    caja(ax, 8.0, 5.72, 1.55, 0.62, "Buscar", BLUE, ec=BLUE, tc="white", bold=True, fs=9.5)
    ax.text(0.45, 5.42, "3 fuentes encontradas  ·  ordenadas por coincidencia",
            fontsize=8, color=MUTED, va="center")

    caja(ax, 0.45, 2.55, 9.1, 2.70, "", "#E7EEF7", ec=BLUE)
    ax.text(0.75, 4.93, "cartera_creditos.mora_producto", fontsize=11, color=NAVY,
            fontweight="bold", va="center", fontfamily=HEAD)
    caja(ax, 7.60, 4.72, 1.70, 0.42, "Fuente oficial", "#166534", ec="#166534",
         tc="white", fs=8, bold=True)
    ax.text(0.75, 4.42,
            "Saldo en mora agrupado por producto de crédito, al cierre de cada día hábil.",
            fontsize=9, color=INK, va="center")

    for etiqueta, valor, x in [
        ("Propietario", "Subgerencia de Información de Crédito", 0.75),
        ("Actualizado", "hoy, 06:15 h", 4.75),
        ("Periodicidad", "diaria (T+1)", 7.15),
    ]:
        ax.text(x, 3.86, etiqueta.upper(), fontsize=7, color=MUTED, va="center",
                fontweight="bold")
        ax.text(x, 3.56, valor, fontsize=8.5, color=INK, va="center")

    caja(ax, 0.75, 2.82, 1.55, 0.45, "Ver dato", BLUE, ec=BLUE, tc="white", fs=8.5, bold=True)
    caja(ax, 2.45, 2.82, 1.65, 0.45, "Ver linaje", "white", ec=BLUE, tc=BLUE, fs=8.5)
    caja(ax, 4.25, 2.82, 1.65, 0.45, "Exportar", "white", ec=BLUE, tc=BLUE, fs=8.5)

    for i, (nombre, nota) in enumerate([
        ("riesgo_credito.mora_ajustada", "definición alterna — usada por Riesgos"),
        ("reportes.mora_mensual", "agregado mensual — derivado del anterior"),
    ]):
        y = 1.68 - i * 0.78
        caja(ax, 0.45, y, 9.1, 0.62, "", "white", ec=LINE)
        ax.text(0.75, y + 0.31, nombre, fontsize=9, color=INK, va="center")
        ax.text(9.25, y + 0.31, nota, fontsize=8, color=MUTED, va="center",
                ha="right", style="italic")

    ax.text(5.0, -0.22,
            "La revelación progresiva mantiene el detalle disponible pero fuera del camino",
            ha="center", fontsize=8, color=MUTED, style="italic")

    fig.tight_layout()
    fig.savefig(f"{OUT}/fig4_concepto_buscador.png", dpi=220, bbox_inches="tight")
    plt.close(fig)


figura_1()
figura_2()
figura_3()
figura_4()
print("OK: 4 figuras en", OUT)
