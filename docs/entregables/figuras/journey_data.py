"""Journey map content for deliverable A2 — single source of truth.

Both renderers import this module: the matplotlib generator and the HTML/CSS
one. Editing a cell here changes every output.
"""

BEFORE = "Antes del uso"
DURING = "Durante el uso"
AFTER = "Después del uso"



# --- Journey content -------------------------------------------------------
# Short form of every lane. The full wording lives in the document; here it
# only has to stay readable at print size.

LAURA = {
    "title": "Journey map de equipo · Laura Méndez",
    "subtitle": "Objetivo: validar una cifra de cartera de crédito y responder con la fuente "
                "citada antes de una reunión   ·   Perfil operativo, persona primaria   ·   "
                "Karisma Data, Equipo 8",
    "truth": 3,
    "stages": [
        {
            "phase": BEFORE, "name": "1. Disparo",
            "actions": "Recibe la solicitud.\nIdentifica concepto y corte.\nDecide dónde buscar.",
            "touchpoints": "Mensajería corporativa,\ncorreo, calendario",
            "thoughts": "«¿Es lo mismo que me\npidieron el mes pasado?\n¿A quién le pregunto?»",
            "emotion": -1,
            "pain": "El punto de partida es la\nmemoria y los contactos,\nno el portal.",
            "opportunity": "Enlace directo desde la\nmensajería y consultas\nguardadas al abrir.",
        },
        {
            "phase": DURING, "name": "2. Acceso",
            "actions": "Inicia sesión.\nEl sistema monta el\nespacio de su rol.",
            "touchpoints": "Pantalla de acceso,\nespacio por rol",
            "thoughts": "«Solo quiero llegar\na la búsqueda.\nOjalá siga mi sesión.»",
            "emotion": 0,
            "pain": "Cada paso extra se paga\ncaro: la tarea real\ntodavía no empieza.",
            "opportunity": "Espacios por rol:\nsesión persistente que\naterriza en el buscador.",
        },
        {
            "phase": DURING, "name": "3. Búsqueda",
            "actions": "Escribe el concepto en\nlenguaje de negocio.\nEvalúa y descarta.",
            "touchpoints": "Buscador unificado,\ntarjetas de resultado,\nfiltros",
            "thoughts": "«¿Significa lo mismo que\nen el reporte anterior?\nHay dos casi iguales.»",
            "emotion": -1,
            "pain": "Variables de nombre\nparecido y miedo a tener\nque explicar el error.",
            "opportunity": "Fuente, propietario y\nvigencia en la tarjeta;\nmarca de versión retirada.",
        },
        {
            "phase": DURING, "name": "4. Validación",
            "actions": "Abre la ficha del catálogo.\nLee definición y nota.\nConfirma la vigencia.",
            "touchpoints": "Ficha del catálogo,\ndefinición, conocimiento\ntribal, propietario",
            "thoughts": "«Si uso la fuente\nequivocada tendré que\nexplicar el error.»",
            "emotion": 2,
            "pain": "La definición vive en un\ncorreo o en la cabeza\nde un especialista.",
            "opportunity": "Conocimiento tribal\npublicado junto al dato,\ncon historial de versiones.",
        },
        {
            "phase": DURING, "name": "5. Profundización",
            "actions": "Filtra por periodo.\nPregunta al asistente.\nRevisa el detalle.",
            "touchpoints": "Filtros, vista de detalle,\nasistente con herramienta\nvisible",
            "thoughts": "«No debería tomar tanto\ntiempo. ¿De dónde sacó\nel asistente ese número?»",
            "emotion": 1,
            "pain": "Filtros técnicos en una\nconsulta simple; cifras\nsin fuente declarada.",
            "opportunity": "Revelación progresiva y\nvisibilidad de la consulta\nde la IA en cada cifra.",
        },
        {
            "phase": DURING, "name": "6. Entrega",
            "actions": "Copia el dato con su\nreferencia. Redacta\ny envía la respuesta.",
            "touchpoints": "Copiado con procedencia,\nexportación ligera,\ncorreo",
            "thoughts": "«Quiero que se vea de\ndónde salió, no solo\nel número.»",
            "emotion": 2,
            "pain": "Copiar pierde el contexto\ny anula el trabajo de\nvalidación anterior.",
            "opportunity": "Copiado con procedencia\ny enlace permanente\nal resultado.",
        },
        {
            "phase": AFTER, "name": "7. Reutilización",
            "actions": "Guarda la consulta.\nRecibe el aviso de cambio\ny revisa el impacto.",
            "touchpoints": "Consultas guardadas,\nnotificación de versión,\nhistorial",
            "thoughts": "«¿El reporte que mandé\nel mes pasado sigue\nsiendo válido?»",
            "emotion": 1,
            "pain": "Nadie se entera del\ncambio hasta que dos\náreas presentan cifras\ndistintas.",
            "opportunity": "Aviso dirigido a quien\ntiene la fuente guardada,\ncon alcance declarado.",
        },
    ],
}

DIEGO = {
    "title": "Journey map individual · Diego Hernández",
    "subtitle": "Objetivo: cruzar créditos, liquidez y derivados por contraparte y dejar el "
                "análisis reejecutable   ·   Perfil analista de datos   ·   "
                "Elaborado por Jacqueline Sarmiento Cervantes",
    "truth": 2,
    "stages": [
        {
            "phase": BEFORE, "name": "1. Encargo",
            "actions": "Recibe la petición del área\nde riesgos. Estima si es\nviable en el plazo.",
            "touchpoints": "Correo, reunión breve\ncon el área solicitante",
            "thoughts": "«¿Estas tres fuentes se\npueden cruzar de verdad\no voy a perder dos días?»",
            "emotion": 0,
            "pain": "No hay forma de estimar\nla viabilidad sin abrir\ncada fuente por separado.",
            "opportunity": "Fichas del catálogo con\ncobertura y periodicidad\nvisibles antes de empezar.",
        },
        {
            "phase": DURING, "name": "2. Descubrimiento",
            "actions": "Busca por tema.\nEncuentra fuentes\nrelacionadas que no conocía.",
            "touchpoints": "Catálogo, fuentes\nrelacionadas, metadatos",
            "thoughts": "«No sabía que derivados\ntenía este conjunto.\n¿Quién más lo usa?»",
            "emotion": 2,
            "pain": "Hoy ese hallazgo depende\nde que un colega lo\nmencione en un pasillo.",
            "opportunity": "Relaciones entre fuentes\nexplícitas en el catálogo:\ndescubrimiento sin favores.",
        },
        {
            "phase": DURING, "name": "3. Conciliación",
            "actions": "Compara granularidad,\nperiodos e identificador\nde contraparte.",
            "touchpoints": "Metadatos, diccionario,\nexplorador analítico",
            "thoughts": "«Liquidez es diaria y\ncrédito mensual: si lo\ncruzo así, sale mal.»",
            "emotion": -1,
            "pain": "La conciliación consume\nla mayor parte del tiempo\ny no aporta análisis.",
            "opportunity": "Aviso de granularidad\nincompatible antes de\nejecutar, no después.",
        },
        {
            "phase": DURING, "name": "4. Prueba",
            "actions": "Ejecuta sobre una\ncontraparte conocida.\nVerifica contra su cálculo.",
            "touchpoints": "Muestra acotada,\nvista previa de resultados",
            "thoughts": "«Prefiero probar con poco\nantes de lanzar el\nvolumen completo.»",
            "emotion": 1,
            "pain": "Sin muestra previa, un\nerror se descubre después\nde una hora de proceso.",
            "opportunity": "Muestra acotada por\nomisión y regla de\nagregación registrada.",
        },
        {
            "phase": DURING, "name": "5. Extracción",
            "actions": "Lanza la exportación\ncompleta y sigue\ntrabajando mientras corre.",
            "touchpoints": "Exportación en segundo\nplano, aviso con enlace\nde descarga",
            "thoughts": "«No quiero quedarme\nmirando una barra de\nprogreso.»",
            "emotion": 1,
            "pain": "Los flujos actuales\nbloquean la sesión con\narchivos pesados.",
            "opportunity": "Trabajo en segundo plano\ncon aviso: la interfaz\nnunca queda bloqueada.",
        },
        {
            "phase": AFTER, "name": "6. Reutilización",
            "actions": "Guarda la consulta\nversionada y comparte\nla referencia.",
            "touchpoints": "Consultas guardadas,\nreferencia compartible,\nhistorial de filtros",
            "thoughts": "«El trimestre que viene\nesto se repite: que no\ndependa de mi memoria.»",
            "emotion": 2,
            "pain": "Reconstruir qué versión\ny qué filtros produjeron\nun número es casi imposible.",
            "opportunity": "Consulta versionada y\ncompartible: el método\nviaja junto al resultado.",
        },
    ],
}

ARTURO = {
    "title": "Journey map individual · Arturo Castañeda",
    "subtitle": "Objetivo: entender una señal de riesgo y poder responder por ella ante la "
                "Junta de Gobierno   ·   Perfil directivo   ·   "
                "Elaborado por Alexandro Mayoral Terán",
    "truth": 3,
    "stages": [
        {
            "phase": BEFORE, "name": "1. Antesala",
            "actions": "Quince minutos antes de\nla Junta abre el portal\ndesde su tableta.",
            "touchpoints": "Tableta institucional,\nacceso al espacio directivo",
            "thoughts": "«Tengo cinco minutos de\nintervención y no puedo\nllegar con dudas.»",
            "emotion": -1,
            "pain": "El tiempo es su recurso\nmás escaso y la revisión\nprevia siempre es tarde.",
            "opportunity": "Espacio directivo que\ncarga al instante, listo\npara lectura, no para uso.",
        },
        {
            "phase": DURING, "name": "2. Lectura",
            "actions": "Revisa los cuatro\nindicadores clave del mes\ny su tendencia.",
            "touchpoints": "Tablero consolidado,\ntarjetas de indicador\ncon variación",
            "thoughts": "«Quiero la tendencia\ndel trimestre, no una\ntabla de mil filas.»",
            "emotion": 1,
            "pain": "Los reportes que recibe\ntraen datos crudos que\nno ayudan a decidir.",
            "opportunity": "Tarjetas predictivas:\npocas cifras, grandes,\ncon su variación.",
        },
        {
            "phase": DURING, "name": "3. Detección",
            "actions": "Nota un alza en uno de\nlos indicadores y decide\nsi es relevante.",
            "touchpoints": "Gráfica de tendencia,\ncomparación con el\nperiodo anterior",
            "thoughts": "«¿Esto es ruido\nestacional o algo que\ndebo señalar hoy?»",
            "emotion": -1,
            "pain": "Sin contexto, cualquier\nmovimiento obliga a\nllamar a tres gerentes.",
            "opportunity": "Señal acompañada de su\nmagnitud y su histórico\nen la misma vista.",
        },
        {
            "phase": DURING, "name": "4. Explicación",
            "actions": "Toca la gráfica y lee la\ntarjeta de contexto y el\nsello de conciliación.",
            "touchpoints": "Tarjeta de contexto del\npropietario, sello de\nconciliación, fecha de corte",
            "thoughts": "«Si me preguntan de\ndónde salió esta cifra,\n¿qué respondo?»",
            "emotion": 2,
            "pain": "Hoy la explicación llega\npor teléfono, si el\ngerente está disponible.",
            "opportunity": "Contexto escrito por el\npropietario junto al dato,\ncon quién lo validó.",
        },
        {
            "phase": AFTER, "name": "5. Exposición",
            "actions": "Pide un resumen de la\nvista, bloquea la tableta\ny entra a la reunión.",
            "touchpoints": "Resumen asistido de la\nvista actual con cita\nde cada cifra",
            "thoughts": "«Entro sabiendo qué voy\na decir del único\nindicador que se movió.»",
            "emotion": 2,
            "pain": "Dos directores con dos\ncifras distintas por usar\ncortes de fecha diferentes.",
            "opportunity": "Resumen de la vista\ncomo contexto del agente,\ncon la fuente de cada cifra.",
        },
    ],
}

XIMENA = {
    "title": "Journey map individual · Ximena Solís Barrera",
    "subtitle": "Objetivo: automatizar un cruce diario por API y sobrevivir a un cambio de "
                "esquema   ·   Perfil integración de aplicaciones   ·   "
                "Elaborado por Arthur Jafed Zizumbo Velasco",
    "truth": 3,
    "stages": [
        {
            "phase": BEFORE, "name": "1. Encargo",
            "actions": "El área de riesgos pide\nun cruce diario que hoy\nse hace a mano.",
            "touchpoints": "Petición del área,\nproceso manual existente",
            "thoughts": "«Automatizar esto ahorra\ncuatro horas a la semana;\nhacerlo mal cuesta el doble.»",
            "emotion": 0,
            "pain": "La práctica actual es\ndescargar archivos y\nguardarlos localmente.",
            "opportunity": "Que el portal compita\ncontra esa costumbre con\nun contrato estable.",
        },
        {
            "phase": DURING, "name": "2. Evaluación",
            "actions": "Revisa las fichas de los\ndos conjuntos y decide\nsi el proyecto es viable.",
            "touchpoints": "Catálogo, definición por\ncampo, periodicidad,\nvalores válidos",
            "thoughts": "«¿Puedo confiar en que\neste campo signifique lo\nmismo el mes que viene?»",
            "emotion": 1,
            "pain": "Encuentra el servicio\npero no la definición\nni sus valores válidos.",
            "opportunity": "Documentación del campo\njunto al servicio: diez\nminutos, no dos correos.",
        },
        {
            "phase": DURING, "name": "3. Habilitación",
            "actions": "Genera credenciales\ndesde su propio perfil,\nsin abrir un ticket.",
            "touchpoints": "Perfil de usuario,\ncredenciales de\nintegración",
            "thoughts": "«Si tengo que pedir\npermiso cada vez, la\ngente lo resuelve por fuera.»",
            "emotion": 2,
            "pain": "Cada fuente nueva implica\nun trámite distinto con\nsu propio responsable.",
            "opportunity": "Autoservicio con el mismo\nalcance que su rol: la\napp no ve más que ella.",
        },
        {
            "phase": DURING, "name": "4. Contrato",
            "actions": "Prueba con un rango corto\ny guarda el contrato de\ndatos en su repositorio.",
            "touchpoints": "Consulta de prueba,\ncontrato de datos con\nversión de esquema",
            "thoughts": "«Quiero una prueba que\ndetecte el cambio antes\nde que rompa producción.»",
            "emotion": 1,
            "pain": "Sin contrato explícito,\nun cambio de tipo se\ndescubre al fallar.",
            "opportunity": "Contrato versionado que\npuede versionarse y\nprobarse desde fuera.",
        },
        {
            "phase": DURING, "name": "5. Automatización",
            "actions": "Programa la ejecución\ndiaria y se suscribe a\nlos avisos de cambio.",
            "touchpoints": "Programación diaria,\nsuscripción a avisos\nde esquema",
            "thoughts": "«El riesgo no está hoy:\nestá en el mes cuatro,\nde madrugada.»",
            "emotion": 1,
            "pain": "El trabajo manual del\nlunes desaparece, pero\nla dependencia crece.",
            "opportunity": "Suscripción por fuente:\nel consumidor decide de\nqué quiere enterarse.",
        },
        {
            "phase": AFTER, "name": "6. Cambio de esquema",
            "actions": "Semanas después llega el\naviso; migra con la\nversión anterior activa.",
            "touchpoints": "Aviso con fecha de\nvigencia, versión anterior\ndisponible",
            "thoughts": "«Menos mal que avisaron\nantes y no cuando ya\nhabía fallado.»",
            "emotion": 2,
            "pain": "Un campo cambia de\nnombre y el proceso falla\nsin que nadie lo anunciara.",
            "opportunity": "Periodo de transición con\nambas versiones vivas:\nmigrar sin prisa.",
        },
    ],
}

MAPS = [
    ("journey_equipo_laura", LAURA),
    ("journey_diego", DIEGO),
    ("journey_arturo", ARTURO),
    ("journey_ximena", XIMENA),
]
