"""Generate the Activity 3 appendix straight from the archived card sorting
sessions, so every line of the appendix is traceable to docs/entregables/datos/.

The appendix is emitted, never hand-written: that is what keeps it auditable.
"""

import json
from pathlib import Path

BASE = Path(__file__).parent
DATOS = BASE / "datos"
SALIDA = BASE / "contenido" / "a3_06_anexo.tex"

PERFIL = {
    "P1": ("Laura Mendez", "Operativo"),
    "P2": ("Diego Hernandez", "Analista"),
    "P3": ("Roberto Valdez", "Propietario de datos"),
    "P4": ("Elena Ruiz", "Auditoria"),
    "P5": ("Jorge Mendieta", "Ingenieria de datos"),
    "P6": ("Arturo Castaneda", "Directivo"),
    "P7": ("Mariana Ovalle Rios", "Administracion"),
    "P8": ("Ximena Solis Barrera", "Integracion"),
}

RUTA_ESPERADA = ["Exploracion", "Exploracion", "Gobierno", "Administracion", "Administracion"]


def esc(texto: str) -> str:
    """Escape the characters LaTeX treats as special."""
    for a, b in [
        ("\\", r"\textbackslash{}"),
        ("&", r"\&"), ("%", r"\%"), ("$", r"\$"), ("#", r"\#"),
        ("_", r"\_"), ("{", r"\{"), ("}", r"\}"),
        ("~", r"\textasciitilde{}"), ("^", r"\textasciicircum{}"),
    ]:
        texto = texto.replace(a, b)
    return texto.replace('"', "''")


tarjetas = {}
for linea in (DATOS / "a3_tarjetas.csv").read_text(encoding="utf-8").splitlines()[1:]:
    if linea.strip():
        partes = linea.split(",")
        tarjetas[partes[0]] = partes[1]

sesiones = {
    pid: json.loads((DATOS / "a3_sorts" / f"{pid}.json").read_text(encoding="utf-8"))
    for pid in PERFIL
}

L = []
w = L.append

w(r"% ============================================================================")
w(r"% Generado por generar_anexo_a3.py a partir de docs/entregables/datos/.")
w(r"% No editar a mano: volver a ejecutar el script.")
w(r"% ============================================================================")
w(r"\section{Anexo. Registro del ejercicio de card sorting}")
w("")
w(
    "Este anexo reproduce el registro de las ocho sesiones aplicadas el 9 de agosto de 2026. "
    "Se incluye para que cualquier lector pueda revisar el material sobre el que se construyeron "
    "las conclusiones de la seccion 2 sin depender de los archivos del repositorio. El contenido "
    "procede de las salidas crudas archivadas en \\texttt{docs/entregables/datos/a3\\_sorts/} y se "
    "reproduce sin editar; la unica normalizacion aplicada fue la restitucion de los signos "
    "diacriticos, que el registro original no conservaba."
)
w("")

# --------------------------------------------------------------- protocolo ---
w(r"\subsection{Protocolo de condicionamiento}")
w("")
w(
    "Cada evaluador recibio la ficha completa de una persona de la Actividad 1 y el mazo de 35 "
    "tarjetas en orden barajado, sin acceso a la arquitectura propuesta ni a las respuestas de los "
    "demas. La plantilla de condicionamiento, comun a las ocho sesiones, fue la siguiente."
)
w("")
w(r"\begin{uxnota}[Plantilla de condicionamiento por persona]")
w(
    "Eres \\textit{[nombre de la persona]}, de \\textit{[edad]} anos, \\textit{[ocupacion]}. "
    "Antecedentes: \\textit{[antecedentes de la ficha de A1]}. Objetivos: \\textit{[objetivos]}. "
    "Puntos de dolor: \\textit{[pain points]}. Habitos con herramientas de datos: \\textit{[habitos]}. "
    "Frase caracteristica: \\textit{[cita de la persona]}."
)
w("")
w(
    "Se te presentan 35 tarjetas de contenido de un portal centralizado de datos financieros. "
    "Agrupalas como tu las organizarias para tu trabajo diario. Tu creas los grupos y tu les pones "
    "nombre, con el vocabulario que usarias en tu area. Cada tarjeta va en un grupo y las 35 deben "
    "quedar colocadas. Agrupa segun tu trabajo y tus dolores, no segun una taxonomia correcta."
)
w("")
w(
    "Al terminar responde: que tarjeta te costo mas ubicar y por que; que tarjetas pondrias en dos "
    "grupos a la vez y por que; y que etiquetas no se entienden en tu vocabulario de trabajo. "
    "Responde en primera persona y justifica cada decision desde tus antecedentes."
)
w(r"\end{uxnota}")
w("")
w(
    "Concluido el sorteo, y solo entonces, se presento la estructura de cuatro modulos propuesta y "
    "se pidio resolver las cinco tareas de la prueba de arbol registradas en el apartado final de "
    "este anexo."
)
w("")

# ------------------------------------------------------- grupos por perfil ---
w(r"\subsection{Agrupaciones y vocabulario de cada evaluador}")
w("")
w(
    "Las tablas siguientes reproducen los grupos que construyo cada evaluador y el nombre que les "
    "dio. Los nombres se transcriben literalmente porque constituyen la evidencia de vocabulario "
    "sobre la que se apoya la seccion 2: ninguno fue sugerido por el instrumento."
)
w("")

for pid, (nombre, perfil) in PERFIL.items():
    d = sesiones[pid]
    w(rf"\subsubsection{{{pid}. {esc(nombre)} ({esc(perfil).lower()})}}")
    w("")
    w(rf"\begin{{uxtabla}}{{|L{{4.1cm}}|Y|}}{{Agrupaciones de {esc(nombre)} ({pid})}}")
    w(r"  \uxheadrow \thd{Nombre que le dio} & \thd{Tarjetas que reunio} \\")
    for g in d["grupos"]:
        etiquetas = "; ".join(tarjetas.get(t, t) for t in g["tarjetas"])
        w(rf"  {esc(g['nombre'])} & {esc(etiquetas)} \\")
    w(r"\end{uxtabla}")
    w("")
    dificil = d["tarjeta_dificil"]
    etiqueta = tarjetas.get(dificil["tarjeta"], dificil["tarjeta"])
    razon = dificil["razon"].strip()
    # La razon del evaluador casi siempre abre nombrando la tarjeta; evitar el eco.
    prefijo = "" if razon.lower().startswith(etiqueta.lower()) else f"{esc(etiqueta)}. "
    w(rf"\textbf{{Tarjeta mas dificil de ubicar.}} {prefijo}{esc(razon)}")
    w("")

# ------------------------------------------------------------- duplicados ---
w(r"\subsection{Peticiones de etiquetado multiple}")
w("")
w(
    "Se registraron 49 peticiones de colocar una misma tarjeta en dos o mas grupos. La tabla reune "
    "las tarjetas solicitadas por tres o mas evaluadores, que son las que originaron las facetas "
    "transversales de la seccion 3, con la razon textual de uno de los evaluadores que la pidio."
)
w("")

conteo = {}
for pid, d in sesiones.items():
    for dup in d["duplicados_solicitados"]:
        conteo.setdefault(dup["tarjeta"], []).append((pid, dup))

w(r"\begin{uxtabla}{|L{2.9cm}|L{1.1cm}|Y|}{Tarjetas con peticion de etiquetado multiple (3 o mas evaluadores)}")
w(r"  \uxheadrow \thd{Tarjeta} & \thd{Evaluadores} & \thd{Razon registrada} \\")
for tid, filas in sorted(conteo.items(), key=lambda kv: -len(kv[1])):
    if len(filas) < 3:
        continue
    pid, dup = filas[0]
    quien = PERFIL[pid][0].split()[0]
    w(
        rf"  {esc(tarjetas.get(tid, tid))} & {len(filas)} de 8 & "
        rf"{esc(dup['razon'])} ({esc(quien)}) \\"
    )
w(r"\end{uxtabla}")
w("")

# -------------------------------------------------------------- etiquetas ---
w(r"\subsection{Etiquetas senaladas como poco claras}")
w("")
w(
    "Los evaluadores marcaron 48 veces alguna etiqueta como ajena a su vocabulario. La tabla ordena "
    "las mas senaladas y recoge un comentario textual de cada una; son las candidatas a renombrarse "
    "antes del prototipado."
)
w("")

conf = {}
for pid, d in sesiones.items():
    for e in d["etiquetas_confusas"]:
        conf.setdefault(e["tarjeta"], []).append((pid, e))

w(r"\begin{uxtabla}{|L{2.9cm}|L{1.1cm}|Y|}{Etiquetas con mas senalamientos de falta de claridad}")
w(r"  \uxheadrow \thd{Etiqueta} & \thd{Evaluadores} & \thd{Comentario registrado} \\")
for tid, filas in sorted(conf.items(), key=lambda kv: -len(kv[1]))[:10]:
    pid, e = filas[0]
    quien = PERFIL[pid][0].split()[0]
    w(
        rf"  {esc(tarjetas.get(tid, tid))} & {len(filas)} de 8 & "
        rf"{esc(e['comentario'])} ({esc(quien)}) \\"
    )
w(r"\end{uxtabla}")
w("")

# ------------------------------------------------------------ prueba arbol ---
w(r"\subsection{Registro de la prueba de arbol}")
w("")
w(
    "Las 40 observaciones que sostienen el apartado de pruebas de la seccion 3. La columna de "
    "coincidencia indica si el primer nivel elegido corresponde al previsto por la arquitectura "
    "puesta a prueba."
)
w("")
# Son 40 filas: no caben en una pagina, asi que va en el entorno que si se parte.
w(
    r"\begin{uxtablalarga}{|L{1.0cm}|L{3.3cm}|L{2.3cm}|Y|L{1.4cm}|}"
    r"{Registro completo de la prueba de arbol}"
    r"{\thd{Ev.} & \thd{Tarea} & \thd{Primer nivel} & \thd{Segundo nivel indicado} & \thd{Coincide}}"
)
for pid in PERFIL:
    for i, item in enumerate(sesiones[pid]["arbol"]):
        coincide = "Si" if item["primer_nivel"] == RUTA_ESPERADA[i] else "No"
        duda = " (titubeo)" if item.get("dudo") else ""
        w(
            rf"  {pid} & {esc(item['tarea'])} & {esc(item['primer_nivel'])}{duda} & "
            rf"{esc(item['segundo_nivel'])} & {coincide} \\"
        )
w(r"\end{uxtablalarga}")
w("")

SALIDA.write_text("\n".join(L) + "\n", encoding="utf-8")
print(f"{SALIDA.name}: {len(L)} lineas, {len('\n'.join(L))} caracteres")
