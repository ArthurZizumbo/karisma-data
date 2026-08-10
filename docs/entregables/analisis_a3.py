"""Quantitative analysis of the A3 synthetic card sorting for Karisma Data.

Reads the eight archived sessions in datos/a3_sorts/, validates them, builds the
35x35 co-occurrence matrix, runs average-linkage hierarchical clustering and
writes three 300 dpi figures plus a JSON summary on stdout.

All counts are absolute over n = 8 prototype evaluators. No percentages.
"""

from __future__ import annotations

import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.patches import Patch
from scipy.cluster.hierarchy import dendrogram, fcluster, leaves_list, linkage
from scipy.spatial.distance import squareform

# --- Institutional palette (mirrors generar_figuras_a3.py) --------------------
COLOR_NAVY = "#1F4D78"
COLOR_BLUE = "#2563EB"
COLOR_SKY = "#3B82F6"
COLOR_AMBER = "#F97316"
COLOR_MUTED = "#64748B"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SORTS_DIR = os.path.join(BASE_DIR, "datos", "a3_sorts")
CARDS_CSV = os.path.join(BASE_DIR, "datos", "a3_tarjetas.csv")
FIG_DIR = os.path.join(BASE_DIR, "figuras")

SESSION_FILES = [f"P{i}.json" for i in range(1, 9)]

# Short profile names used in every narrative output.
PERFILES = {
    "P1": "Laura (operativo)",
    "P2": "Diego (analista)",
    "P3": "Roberto (propietario de datos)",
    "P4": "Elena (auditoria)",
    "P5": "Jorge (ingenieria)",
    "P6": "Arturo (directivo)",
    "P7": "Mariana (administracion)",
    "P8": "Ximena (integracion)",
}

# Expected first-level route for the tree test (analysis rule of the brief).
RUTAS_ESPERADAS = {
    "Localizar una fuente de liquidez": "Exploracion",
    "Exportar la cartera de credito": "Exploracion",
    "Consultar un indicador de riesgo": "Gobierno",
    "Revisar quien autorizo un acceso": "Administracion",
    "Crear una credencial de integracion": "Administracion",
}

# Number of canonical clusters cut from the dendrogram.
K_CLUSTERS = 9

# Human-readable name proposed for each canonical cluster, keyed by the sorted
# tuple of its member card ids. Filled after the first exploratory run; any
# cluster without an entry falls back to an automatic name built from the most
# frequent terms in the evaluator group names that map onto it.
NOMBRES_CLUSTER = {
    ("T07", "T08", "T09", "T10", "T11", "T12"): "Datos financieros por materia",
    ("T21", "T22", "T23"): "Tableros e indicadores de riesgo",
    ("T32", "T33", "T34"): "Integracion tecnica: API y conectores",
    ("T24", "T25", "T26", "T29", "T30", "T31"): "Accesos, permisos y autorizaciones",
    ("T19", "T35"): "Calidad y actualizacion del dato",
    ("T06", "T16", "T17", "T18", "T20"): "Documentacion y significado del dato",
    ("T01", "T13", "T14", "T15", "T27", "T28"): "Consultar, exportar y compartir",
    ("T02", "T03"): "Mis consultas guardadas",
    ("T04", "T05"): "Mi cuenta y mis avisos",
}

STOPWORDS = {
    "de", "del", "la", "el", "los", "las", "y", "o", "a", "en", "que", "para",
    "con", "por", "lo", "un", "una", "unos", "unas", "se", "al", "es", "no",
    "me", "sin", "como", "ya", "antes", "sobre", "su", "sus", "le", "ni",
    "cada", "todo", "toda", "donde", "cuando", "si", "mas", "muy", "hasta",
    "e", "u", "the",
}


# --- Helpers -----------------------------------------------------------------
def strip_accents(text: str) -> str:
    """Return text without diacritics, lowercased."""
    norm = unicodedata.normalize("NFD", text)
    return "".join(c for c in norm if unicodedata.category(c) != "Mn").lower()


def stem(word: str) -> str:
    """Very small Spanish plural stemmer, enough for group-name term counts."""
    if len(word) > 4 and word.endswith("es"):
        return word[:-2]
    if len(word) > 3 and word.endswith("s"):
        return word[:-1]
    return word


def tokenize(name: str) -> list[str]:
    """Split a group name into meaningful stems."""
    clean = re.sub(r"\(.*?\)", " ", name)
    words = re.findall(r"[a-zA-ZÀ-ſ]+", strip_accents(clean))
    return [stem(w) for w in words if w not in STOPWORDS and len(w) > 2]


def load_cards() -> dict[str, dict[str, str]]:
    """Load the 35 cards, preserving id -> label/definition."""
    cards: dict[str, dict[str, str]] = {}
    with open(CARDS_CSV, encoding="utf-8") as handle:
        header = handle.readline()
        if not header.lower().startswith("id,"):
            print(f"[AVISO] cabecera inesperada en a3_tarjetas.csv: {header!r}")
        for line in handle:
            line = line.rstrip("\n")
            if not line.strip():
                continue
            parts = line.split(",", 2)
            if len(parts) < 3:
                print(f"[AVISO] fila mal formada en a3_tarjetas.csv: {line!r}")
                continue
            cid, etiqueta, definicion = parts
            cards[cid.strip()] = {
                "etiqueta": etiqueta.strip(),
                "definicion": definicion.strip(),
            }
    return cards


def load_sessions(card_ids: list[str]) -> tuple[list[dict], list[str]]:
    """Load and validate the eight sessions. Never aborts on data problems."""
    sessions: list[dict] = []
    incidencias: list[str] = []
    expected = set(card_ids)
    for fname in SESSION_FILES:
        path = os.path.join(SORTS_DIR, fname)
        pid = fname.split(".")[0]
        if not os.path.exists(path):
            msg = f"[VALIDACION] {pid}: archivo ausente ({path}); sesion omitida."
            print(msg)
            incidencias.append(msg)
            continue
        with open(path, encoding="utf-8") as handle:
            data = json.load(handle)
        placed: list[str] = []
        for grupo in data.get("grupos", []):
            placed.extend(grupo.get("tarjetas", []))
        counts = Counter(placed)
        faltantes = sorted(expected - set(placed))
        repetidas = sorted(t for t, c in counts.items() if c > 1)
        desconocidas = sorted(set(placed) - expected)
        if faltantes:
            msg = f"[VALIDACION] {pid} ({PERFILES.get(pid, '?')}): faltan {faltantes}"
            print(msg)
            incidencias.append(msg)
        if repetidas:
            msg = f"[VALIDACION] {pid} ({PERFILES.get(pid, '?')}): repetidas {repetidas}"
            print(msg)
            incidencias.append(msg)
        if desconocidas:
            msg = f"[VALIDACION] {pid} ({PERFILES.get(pid, '?')}): ids fuera del mazo {desconocidas}"
            print(msg)
            incidencias.append(msg)
        if not faltantes and not repetidas and not desconocidas:
            print(f"[VALIDACION] {pid} ({PERFILES.get(pid, '?')}): 35/35 tarjetas colocadas, sin repeticiones.")
        data["_pid"] = pid
        data["_perfil"] = PERFILES.get(pid, pid)
        sessions.append(data)
    return sessions, incidencias


def wrap(text: str, width: int) -> str:
    """Wrap a label into at most two lines for figure readability."""
    if len(text) <= width:
        return text
    words = text.split()
    line, lines = "", []
    for word in words:
        if len(line) + len(word) + 1 <= width:
            line = f"{line} {word}".strip()
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return "\n".join(lines)


# --- Core analysis -----------------------------------------------------------
def build_cooccurrence(sessions: list[dict], card_ids: list[str]) -> np.ndarray:
    """Count, per card pair, how many evaluators put them in the same group."""
    idx = {cid: i for i, cid in enumerate(card_ids)}
    n = len(card_ids)
    matrix = np.zeros((n, n), dtype=float)
    for data in sessions:
        seen: set[str] = set()
        for grupo in data.get("grupos", []):
            miembros = [t for t in dict.fromkeys(grupo.get("tarjetas", [])) if t in idx]
            miembros = [t for t in miembros if t not in seen]
            seen.update(miembros)
            for a in miembros:
                for b in miembros:
                    matrix[idx[a], idx[b]] += 1
    return matrix


def canonical_assignment(sessions, card_ids, cluster_of):
    """Map every evaluator group to the canonical cluster of its majority.

    Returns (asignacion, grupos_por_cluster) where asignacion[card][pid] is the
    canonical cluster id that this evaluator effectively assigned the card to.
    """
    asignacion: dict[str, dict[str, int]] = defaultdict(dict)
    grupos_por_cluster: dict[int, list[str]] = defaultdict(list)
    for data in sessions:
        pid = data["_pid"]
        for grupo in data.get("grupos", []):
            miembros = [t for t in grupo.get("tarjetas", []) if t in cluster_of]
            if not miembros:
                continue
            votos = Counter(cluster_of[t] for t in miembros)
            top = max(votos.values())
            dominante = min(c for c, v in votos.items() if v == top)
            grupos_por_cluster[dominante].append(grupo.get("nombre", ""))
            for t in miembros:
                asignacion[t][pid] = dominante
    return asignacion, grupos_por_cluster


def main() -> int:
    os.makedirs(FIG_DIR, exist_ok=True)
    cards = load_cards()
    card_ids = sorted(cards)
    n_cards = len(card_ids)
    print(f"[INFO] mazo cargado: {n_cards} tarjetas desde {CARDS_CSV}")

    sessions, incidencias = load_sessions(card_ids)
    n_eval = len(sessions)
    print(f"[INFO] sesiones cargadas: {n_eval}")
    if n_eval == 0:
        print("[ERROR] no hay sesiones que analizar.")
        return 1

    etiquetas = [cards[c]["etiqueta"] for c in card_ids]
    co = build_cooccurrence(sessions, card_ids)

    # Distance = 1 - (co-occurrence / 8); zero diagonal, symmetric.
    dist = 1.0 - (co / float(n_eval))
    np.fill_diagonal(dist, 0.0)
    dist = (dist + dist.T) / 2.0
    condensed = squareform(dist, checks=False)
    Z = linkage(condensed, method="average")
    orden = leaves_list(Z)

    labels_cluster = fcluster(Z, t=K_CLUSTERS, criterion="maxclust")
    cluster_of = {card_ids[i]: int(labels_cluster[i]) for i in range(n_cards)}

    asignacion, grupos_por_cluster = canonical_assignment(sessions, card_ids, cluster_of)

    # --- Cluster cohesion ---------------------------------------------------
    clusteres = []
    for cid in sorted(int(c) for c in set(labels_cluster)):
        miembros = [card_ids[i] for i in range(n_cards) if labels_cluster[i] == cid]
        idxs = [card_ids.index(m) for m in miembros]
        if len(idxs) > 1:
            vals = [co[a, b] for i, a in enumerate(idxs) for b in idxs[i + 1:]]
            cohesion = float(np.mean(vals))
            minimo = float(np.min(vals))
        else:
            cohesion = float("nan")
            minimo = float("nan")
        nombres = grupos_por_cluster.get(cid, [])
        terminos = Counter()
        for nombre in nombres:
            for tok in set(tokenize(nombre)):
                terminos[tok] += 1
        auto = " / ".join(t for t, _ in terminos.most_common(3)) or f"Cluster {cid}"
        propuesto = NOMBRES_CLUSTER.get(tuple(sorted(miembros)), auto)
        clusteres.append({
            "id": cid,
            "nombre_propuesto": propuesto,
            "tarjetas": [f"{m} {cards[m]['etiqueta']}" for m in miembros],
            "cohesion_media_sobre_8": round(cohesion, 2) if cohesion == cohesion else None,
            "cohesion_minima_sobre_8": round(minimo, 2) if minimo == minimo else None,
            "nombres_de_grupo_que_lo_originan": sorted(set(nombres)),
        })

    # --- Duplicates requested ----------------------------------------------
    dup_por_tarjeta: dict[str, dict] = defaultdict(lambda: {"pids": [], "razones": []})
    for data in sessions:
        pid = data["_pid"]
        for dup in data.get("duplicados_solicitados", []):
            t = dup.get("tarjeta")
            if t not in cards:
                print(f"[VALIDACION] {pid}: duplicado sobre tarjeta desconocida {t!r}")
                continue
            dup_por_tarjeta[t]["pids"].append(pid)
            dup_por_tarjeta[t]["razones"].append(f"{PERFILES[pid]}: {dup.get('razon', '').strip()}")
    duplicados = []
    for t, info in sorted(dup_por_tarjeta.items(), key=lambda kv: (-len(kv[1]["pids"]), kv[0])):
        duplicados.append({
            "tarjeta": t,
            "etiqueta": cards[t]["etiqueta"],
            "n_evaluadores_que_lo_pidieron": len(info["pids"]),
            "perfiles": [PERFILES[p] for p in info["pids"]],
            "razones": info["razones"],
        })

    # --- Cards in dispute ---------------------------------------------------
    disputa = []
    for t in card_ids:
        por_pid = asignacion.get(t, {})
        votos = Counter(por_pid.values())
        n_grupos = len(votos)
        pidio_dup = t in dup_por_tarjeta
        if n_grupos >= 2 or pidio_dup:
            reparto_txt = "; ".join(
                f"{next(c['nombre_propuesto'] for c in clusteres if c['id'] == cl)}: "
                + ", ".join(PERFILES[p] for p in sorted(por_pid) if por_pid[p] == cl)
                for cl, _ in votos.most_common()
            )
            disputa.append({
                "tarjeta": t,
                "etiqueta": cards[t]["etiqueta"],
                "n_grupos_distintos": n_grupos,
                "n_evaluadores_en_el_grupo_mayoritario": max(votos.values()) if votos else 0,
                "n_evaluadores_fuera_del_mayoritario": (n_eval - max(votos.values())) if votos else n_eval,
                "duplicado_solicitado_por": len(dup_por_tarjeta.get(t, {}).get("pids", [])),
                "reparto": reparto_txt,
                "votos": {int(cl): int(v) for cl, v in votos.items()},
            })
    disputa.sort(key=lambda d: (-d["n_evaluadores_fuera_del_mayoritario"], -d["n_grupos_distintos"], d["tarjeta"]))

    # --- Group-name term frequency -----------------------------------------
    term_eval: dict[str, set[str]] = defaultdict(set)
    for data in sessions:
        pid = data["_pid"]
        for grupo in data.get("grupos", []):
            for tok in set(tokenize(grupo.get("nombre", ""))):
                term_eval[tok].add(pid)
    terminos = [
        {
            "termino": t,
            "n_evaluadores_que_lo_usaron": len(pids),
            "evaluadores": [PERFILES[p] for p in sorted(pids)],
        }
        for t, pids in sorted(term_eval.items(), key=lambda kv: (-len(kv[1]), kv[0]))
        if len(pids) >= 2
    ]

    # --- Tree test ----------------------------------------------------------
    arbol = []
    for tarea, esperado in RUTAS_ESPERADAS.items():
        respuestas: dict[str, str] = {}
        dudas: list[str] = []
        for data in sessions:
            for item in data.get("arbol", []):
                if item.get("tarea") == tarea:
                    respuestas[data["_pid"]] = item.get("primer_nivel", "(sin dato)")
                    if item.get("dudo"):
                        dudas.append(data["_pid"])
        faltan = [d["_pid"] for d in sessions if d["_pid"] not in respuestas]
        if faltan:
            print(f"[VALIDACION] tarea {tarea!r} sin respuesta en: {faltan}")
        aciertos = [p for p, v in respuestas.items() if v == esperado]
        reparto = defaultdict(list)
        for p, v in respuestas.items():
            reparto[v].append(p)
        arbol.append({
            "tarea": tarea,
            "ruta_esperada_primer_nivel": esperado,
            "aciertos_sobre_8": len(aciertos),
            "aciertan": [PERFILES[p] for p in sorted(aciertos)],
            "reparto_de_primer_nivel": {
                k: [PERFILES[p] for p in sorted(v)] for k, v in
                sorted(reparto.items(), key=lambda kv: -len(kv[1]))
            },
            "declararon_duda_sobre_8": len(dudas),
            "dudaron": [PERFILES[p] for p in sorted(dudas)],
        })

    # --- Confusing labels ---------------------------------------------------
    conf: dict[str, dict] = defaultdict(lambda: {"pids": [], "comentarios": []})
    for data in sessions:
        pid = data["_pid"]
        for item in data.get("etiquetas_confusas", []):
            t = item.get("tarjeta")
            if t not in cards:
                print(f"[VALIDACION] {pid}: etiqueta confusa sobre tarjeta desconocida {t!r}")
                continue
            conf[t]["pids"].append(pid)
            conf[t]["comentarios"].append(f"{PERFILES[pid]}: {item.get('comentario', '').strip()}")
    etiquetas_confusas = [
        {
            "tarjeta": t,
            "etiqueta": cards[t]["etiqueta"],
            "n_menciones_sobre_8": len(info["pids"]),
            "perfiles": [PERFILES[p] for p in info["pids"]],
            "comentarios": info["comentarios"],
        }
        for t, info in sorted(conf.items(), key=lambda kv: (-len(kv[1]["pids"]), kv[0]))
    ]

    # --- Hardest card -------------------------------------------------------
    dificiles = Counter()
    dificil_detalle = defaultdict(list)
    for data in sessions:
        td = data.get("tarjeta_dificil") or {}
        t = td.get("tarjeta")
        if t in cards:
            dificiles[t] += 1
            dificil_detalle[t].append(PERFILES[data["_pid"]])

    # --- Figures ------------------------------------------------------------
    figuras = []
    figuras.append(fig_matriz(co, orden, etiquetas, labels_cluster, n_eval))
    figuras.append(fig_dendrograma(Z, etiquetas, labels_cluster, card_ids, n_eval))
    figuras.append(fig_disputa(disputa, clusteres, n_eval))

    resumen = {
        "n_evaluadores": n_eval,
        "n_tarjetas": n_cards,
        "nota_metodologica": (
            "Evaluadores prototipo sinteticos (LLM condicionado por persona), pre-validacion "
            "complementaria; nunca sustituto de la prueba con usuarios reales. Todos los conteos "
            "son absolutos sobre 8."
        ),
        "incidencias_de_validacion": incidencias or ["ninguna: las 8 sesiones colocaron las 35 tarjetas sin repetir"],
        "tarjetas_en_disputa": disputa,
        "duplicados_solicitados_por_tarjeta": duplicados,
        "frecuencia_de_terminos_en_nombres_de_grupo": terminos,
        "clusteres_detectados": clusteres,
        "prueba_de_arbol": arbol,
        "etiquetas_confusas": etiquetas_confusas,
        "tarjeta_mas_dificil": [
            {"tarjeta": t, "etiqueta": cards[t]["etiqueta"], "n_menciones_sobre_8": c,
             "perfiles": dificil_detalle[t]}
            for t, c in dificiles.most_common()
        ],
        "figuras_generadas": figuras,
    }

    print("\n===== RESUMEN JSON =====")
    print(json.dumps(resumen, ensure_ascii=False, indent=2))
    return 0

def fig_matriz(co, orden, etiquetas, labels_cluster, n_eval) -> str:
    """35x35 heatmap ordered by dendrogram leaves, with cluster blocks outlined."""
    data = co[np.ix_(orden, orden)].copy()
    np.fill_diagonal(data, float(n_eval))
    labs = [etiquetas[i] for i in orden]
    clus = [labels_cluster[i] for i in orden]
    cmap = LinearSegmentedColormap.from_list(
        "karisma", ["#FFFFFF", "#DCE6F1", "#9CB9DA", COLOR_SKY, COLOR_BLUE, COLOR_NAVY]
    )
    fig, ax = plt.subplots(figsize=(7.6, 7.9))
    im = ax.imshow(data, cmap=cmap, vmin=0, vmax=n_eval, interpolation="nearest")
    ax.set_xticks(range(len(labs)))
    ax.set_yticks(range(len(labs)))
    ax.set_xticklabels(labs, rotation=90, fontsize=5.8, color=COLOR_NAVY)
    ax.set_yticklabels(labs, fontsize=5.8, color=COLOR_NAVY)
    ax.set_xticks(np.arange(-0.5, len(labs), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(labs), 1), minor=True)
    ax.grid(which="minor", color="#FFFFFF", linewidth=0.4)
    ax.tick_params(which="minor", length=0)
    ax.tick_params(which="major", length=2, color=COLOR_MUTED)
    for i in range(len(labs)):
        for j in range(len(labs)):
            v = int(round(data[i, j]))
            if v >= 6 and i != j:
                ax.text(j, i, str(v), ha="center", va="center", fontsize=4.0,
                        color="white" if v >= 7 else COLOR_NAVY)
    # Outline each cluster block so the structure also reads in black and white.
    inicio = 0
    for k in range(1, len(clus) + 1):
        if k == len(clus) or clus[k] != clus[inicio]:
            ancho = k - inicio
            ax.add_patch(plt.Rectangle((inicio - 0.5, inicio - 0.5), ancho, ancho,
                                       fill=False, edgecolor=COLOR_AMBER, linewidth=1.4))
            inicio = k
    ax.set_title(
        "Matriz de similitud del card sorting de Karisma Data\n"
        f"Coincidencias por par de tarjetas (n = {n_eval} evaluadores prototipo)",
        fontsize=11, fontweight="bold", color=COLOR_NAVY, pad=26,
    )
    ax.text(0.0, 1.012,
            "Orden de filas y columnas = orden de hojas del dendrograma de enlace promedio. "
            "Los recuadros marcan los clusteres.",
            transform=ax.transAxes, fontsize=6.4, color=COLOR_MUTED)
    cbar = fig.colorbar(im, ax=ax, fraction=0.032, pad=0.02, ticks=range(0, n_eval + 1))
    cbar.set_label(f"Evaluadores que agruparon juntas las dos tarjetas (0 a {n_eval})",
                   fontsize=7.5, color=COLOR_NAVY)
    cbar.ax.tick_params(labelsize=7, color=COLOR_NAVY)
    path = os.path.join(FIG_DIR, "a3_matriz_similitud.png")
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    return path


def fig_dendrograma(Z, etiquetas, labels_cluster, card_ids, n_eval) -> str:
    """Average-linkage dendrogram with institutional link colours."""
    from scipy.cluster.hierarchy import set_link_color_palette

    set_link_color_palette([COLOR_NAVY, COLOR_BLUE, COLOR_SKY, COLOR_AMBER,
                            "#0F172A", COLOR_NAVY, COLOR_BLUE, COLOR_SKY,
                            COLOR_AMBER, "#0F172A"])
    fig, ax = plt.subplots(figsize=(7.4, 9.3))
    # Threshold that reproduces exactly the k clusters reported in the summary.
    alturas = np.sort(Z[:, 2])
    k_real = len(set(int(c) for c in labels_cluster))
    corte = (alturas[-k_real] + alturas[-(k_real - 1)]) / 2.0
    dendrogram(
        Z,
        labels=[f"{card_ids[i]}  {etiquetas[i]}" for i in range(len(etiquetas))],
        orientation="left",
        color_threshold=corte,
        above_threshold_color="#A9B4C2",
        leaf_font_size=7.2,
        ax=ax,
    )
    # Leave a sliver past zero so groups that merge at distance 0 stay visible.
    xl = ax.get_xlim()
    ax.set_xlim(xl[0], -0.03)
    ax.axvline(corte, color=COLOR_AMBER, linestyle="--", linewidth=1.1)
    ax.text(corte, ax.get_ylim()[0], f" corte en {k_real} clusteres ", color=COLOR_AMBER,
            fontsize=7.5, va="bottom", ha="left")
    ax.set_title(
        "Dendrograma del card sorting de Karisma Data\n"
        f"Enlace promedio sobre distancia 1 - (coincidencias / {n_eval}); "
        f"n = {n_eval} evaluadores prototipo",
        fontsize=11, fontweight="bold", color=COLOR_NAVY, pad=22,
    )
    ax.text(0.0, 1.008,
            f"Distancia 0 = las {n_eval} sesiones la pusieron en el mismo grupo; "
            "distancia 1 = ninguna sesion las junto.",
            transform=ax.transAxes, fontsize=6.4, color=COLOR_MUTED)
    ax.set_xlabel(f"Distancia = 1 - (evaluadores que las agruparon juntas / {n_eval})",
                  fontsize=8.5, color=COLOR_NAVY)
    ax.tick_params(axis="y", colors=COLOR_NAVY)
    ax.tick_params(axis="x", colors=COLOR_NAVY, labelsize=7.5)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(COLOR_MUTED)
    ax.grid(axis="x", linestyle=":", linewidth=0.5, color=COLOR_MUTED, alpha=0.6)
    ax.set_axisbelow(True)
    path = os.path.join(FIG_DIR, "a3_dendrograma.png")
    fig.savefig(path, dpi=300, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    set_link_color_palette(None)
    return path


def fig_disputa(disputa, clusteres, n_eval) -> str:
    """Stacked horizontal bars for the contested cards."""
    from matplotlib import patheffects

    nombre_cluster = {c["id"]: c["nombre_propuesto"] for c in clusteres}
    filas = list(disputa)
    filas.reverse()  # highest disagreement on top once barh flips the axis
    ids_cluster = sorted({cl for f in filas for cl in f["votos"]})
    colores = [COLOR_NAVY, COLOR_BLUE, COLOR_SKY, COLOR_AMBER, COLOR_MUTED,
               "#0F172A", "#A7C7F2", "#FBC49B", "#CBD5E1", "#1E293B"]
    hatches = ["", "//", "..", "xx", "\\\\", "++", "oo", "--", "**", "||"]
    claros = {COLOR_SKY, COLOR_AMBER, COLOR_MUTED, "#A7C7F2", "#FBC49B", "#CBD5E1"}
    estilo = {cl: (colores[i % len(colores)], hatches[i % len(hatches)])
              for i, cl in enumerate(ids_cluster)}

    fig, ax = plt.subplots(figsize=(8.0, 10.0))
    fig.subplots_adjust(left=0.29, right=0.985, top=0.898, bottom=0.185)
    y = np.arange(len(filas))
    izq = np.zeros(len(filas))
    for cl in ids_cluster:
        vals = np.array([f["votos"].get(cl, 0) for f in filas], dtype=float)
        color, hatch = estilo[cl]
        ax.barh(y, vals, left=izq, height=0.68, color=color, hatch=hatch,
                edgecolor="white", linewidth=0.7)
        for yi, (v, l) in enumerate(zip(vals, izq)):
            if v > 0:
                txt = ax.text(l + v / 2, yi, str(int(v)), ha="center", va="center",
                              fontsize=7.5, fontweight="bold",
                              color="#111827" if color in claros else "white")
                txt.set_path_effects([
                    patheffects.withStroke(
                        linewidth=1.8,
                        foreground="white" if color in claros else color)
                ])
        izq += vals

    etiquetas_y = []
    for f in filas:
        marca = f"  [dup x{f['duplicado_solicitado_por']}]" if f["duplicado_solicitado_por"] else ""
        etiquetas_y.append(f"{f['tarjeta']}  {f['etiqueta']}{marca}")
    ax.set_yticks(y)
    ax.set_yticklabels(etiquetas_y, fontsize=7.2, color=COLOR_NAVY)
    ax.set_ylim(-0.7, len(filas) - 0.3)
    ax.set_xlim(0, n_eval)
    ax.set_xticks(range(0, n_eval + 1))
    ax.set_xlabel(f"Numero de evaluadores (conteo absoluto sobre {n_eval})",
                  fontsize=9, color=COLOR_NAVY)

    # Separate the cards that only carry a duplicate request from the split ones.
    frontera = [i for i, f in enumerate(filas) if f["n_grupos_distintos"] >= 2]
    if frontera and min(frontera) > 0:
        yline = min(frontera) - 0.5
        ax.axhline(yline, color=COLOR_MUTED, linestyle="-", linewidth=1.0)

    fig.suptitle(
        "Tarjetas en disputa del card sorting de Karisma Data\n"
        f"Reparto entre agrupaciones canonicas (n = {n_eval} evaluadores prototipo)",
        fontsize=12, fontweight="bold", color=COLOR_NAVY, y=0.988, va="top",
    )
    fig.text(0.5, 0.938,
             "Incluye toda tarjeta que quedo en 2 o mas agrupaciones distintas o para la que alguien "
             "pidio duplicado ([dup xN] = cuantos lo pidieron).\n"
             "Bajo la linea horizontal: tarjetas sin division de grupo, incluidas solo por la peticion "
             "de duplicado. Orden: mayor desacuerdo arriba.",
             ha="center", va="top", fontsize=6.8, color=COLOR_MUTED)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(COLOR_MUTED)
    ax.tick_params(axis="x", colors=COLOR_NAVY, labelsize=8)
    ax.grid(axis="x", linestyle=":", linewidth=0.5, color=COLOR_MUTED, alpha=0.6)
    ax.set_axisbelow(True)

    handles = [Patch(facecolor=estilo[cl][0], hatch=estilo[cl][1], edgecolor="white",
                     label=nombre_cluster.get(cl, f"Cluster {cl}"))
               for cl in ids_cluster]
    fig.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 0.012),
               ncol=3, fontsize=7.2, frameon=False, title="Agrupacion canonica",
               title_fontsize=8.2, handlelength=2.2, columnspacing=1.4,
               labelspacing=0.7)
    path = os.path.join(FIG_DIR, "a3_disputa.png")
    fig.savefig(path, dpi=300, facecolor="white")
    plt.close(fig)
    return path


if __name__ == "__main__":
    sys.exit(main())
