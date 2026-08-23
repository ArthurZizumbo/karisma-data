#!/bin/sh
# ---------------------------------------------------------------------------
#  US-AVANCE-5 - el repositorio publico no publica la direccion del demo.
#
#  Este repositorio es publico y la direccion de Cloud Run del demo lleva
#  dentro un identificador del proyecto de GCP: el hash de la forma antigua
#  -servicio-HASH-uc.a.run.app- y el numero de proyecto de la nueva
#  -servicio-NNNNNNNNNNNN.region.run.app-. Ninguno da acceso por si solo, pero
#  los dos son superficie de abuso de facturacion y de ingenieria social, y la
#  regla del repositorio es citarlos por variable, nunca por valor.
#
#  No es una hipotesis: ya paso. El commit 63a3b9f corrigio docs/us-m01.md,
#  que publicaba las dos direcciones con el identificador dentro, y lo hizo a
#  mano, antes de empujar y sin reescribir la historia. Esta comprobacion es lo
#  que ahi falto.
#
#  La mecanica correcta es la macro \urlDemoWeb de docs/entregables/datos/demo.tex,
#  cuyo valor vive en datos/despliegue.tex, que .gitignore excluye.
#
#  POR QUE NO ES UNA REGLA DE .gitleaks.toml, que seria su sitio natural:
#  "gitleaks dir" recorre el ARBOL DE TRABAJO, no el indice, y en el arbol hay
#  dos artefactos locales que legitimamente contienen la direccion -el propio
#  datos/despliegue.tex y los .txt y .log que latexmk deja en
#  docs/entregables/tmp/-. Una regla ahi obligaria a dos entradas nuevas en la
#  lista de permitidos, que es justo donde el archivo advierte que un escaneo
#  se vuelve teatro. La pregunta que importa -que publica el repositorio- se
#  responde sobre "git ls-files" y no necesita ninguna excepcion.
#
#  Cuatro comprobaciones, porque las cuatro pueden fallar por separado:
#    0. .gitignore sigue apartando datos/despliegue.tex y sigue versionando su
#       plantilla. Es la condicion de la que dependen las otras tres.
#    1. El patron DETECTA las dos formas de la direccion.
#    2. El patron NO marca los marcadores de posicion ni las direcciones
#       ficticias que ya usan la plantilla y las pruebas del frontend.
#    3. Ningun archivo de texto que el repositorio vaya a publicar la contiene:
#       lo versionado y lo que esta sin versionar y sin ignorar.
#
#  Fuera de alcance, y es una decision, no un descuido: los PDF versionados de
#  docs/semana_*/ son artefactos compilados que IMPRIMEN la direccion a
#  proposito -el evaluador la necesita- y sus enlaces viajan en flujos
#  comprimidos que ningun grep de texto lee. Quien publique el PDF decide eso;
#  este guion vigila las fuentes.
#
#  POSIX sh, sin argumentos y sin modos. No escribe nada.
# ---------------------------------------------------------------------------

set -eu

RAIZ=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)

# Las dos formas que emite Cloud Run, en una sola alternancia:
#
#   https://servicio-HASH-uc.a.run.app             (antigua, hash del proyecto)
#   https://servicio-NUMERO.us-central1.run.app    (nueva, numero de proyecto)
#
# HASH y NUMERO van con esas palabras y no con un valor de ejemplo porque este
# archivo tambien pasa por la comprobacion 3 y una direccion completa dentro de
# un comentario la habria puesto roja. Ocurrio al escribirlo.
#
# El patron pide el separador y la longitud de las dos partes variables, y por
# eso no alcanza a "karisma-api-xyz.a.run.app" ni a "servicio-1.a.run.app", que
# son los nombres ficticios que ya usan tres specs del frontend. Que no los
# alcance se comprueba abajo: un patron mas ancho volveria roja una prueba
# legitima, y de ahi a borrar esta barrera hay un paso.
PATRON='https?://[A-Za-z0-9-]+-([A-Za-z0-9]{8,}-[a-z]{2,3}\.a\.run\.app|[0-9]{9,}\.[A-Za-z0-9-]+\.run\.app)'

echo "Verificacion de la direccion del demo (US-AVANCE-5)"
echo ""

# --- 0. La condicion: git sigue apartando el archivo del valor ---------------
# Que datos/despliegue.tex este ignorado no es una promesa, es una condicion, y
# las condiciones se comprueban -es la misma doctrina con la que
# scripts/verificar_gitleaks.sh vigila la excepcion de .env.local-. Si alguien
# reescribe esa linea de .gitignore, o aparece antes una regla mas ancha sobre
# datos/, el archivo pasa a ser un candidato mas de "git add -A" y la direccion
# se publica sin que nadie teclee nada. "git check-ignore" no necesita que el
# archivo exista, asi que esto responde igual en un clon limpio.
IGNORADO='docs/entregables/datos/despliegue.tex'
PLANTILLA='docs/entregables/datos/despliegue.tex.example'

if ! (cd "$RAIZ" && git check-ignore -q "$IGNORADO"); then
    echo "FALLA: git ya NO ignora $IGNORADO." >&2
    echo "Ese archivo lleva la direccion del demo con el identificador del" >&2
    echo "proyecto dentro. Devuelvelo a .gitignore antes de cualquier commit," >&2
    echo "y si ya entro al indice, sacalo con 'git rm --cached'." >&2
    exit 1
fi

if (cd "$RAIZ" && git check-ignore -q "$PLANTILLA"); then
    echo "FALLA: git ignora $PLANTILLA." >&2
    echo "La plantilla es la mitad versionada del contrato: sin ella nadie sabe" >&2
    echo "que forma tiene el valor. La linea de negacion de .gitignore existe" >&2
    echo "justo para esto." >&2
    exit 1
fi

echo "  git aparta el archivo del valor y conserva su plantilla"

# --- 1. El patron detecta ---------------------------------------------------
# Las muestras se componen en tiempo de ejecucion y nunca aparecen enteras en
# el archivo: con la direccion literal escrita aqui, este mismo guion seria el
# primero en fallar su propia comprobacion 3. Es la misma disciplina de
# scripts/verificar_gitleaks.sh con su fixture.
esquema='https://'
servicio='karisma-web'
media_a='1098'
media_b='76543210'

muestra_antigua="${esquema}${servicio}-nx4qz7wtld-uc.a.run.app"
muestra_nueva="${esquema}${servicio}-${media_a}${media_b}.us-central1.run.app"

for muestra in "$muestra_antigua" "$muestra_nueva"; do
    if ! printf '%s\n' "$muestra" | grep -qE "$PATRON"; then
        echo "FALLA: el patron no reconoce una direccion de Cloud Run." >&2
        echo "Muestra que deberia marcar: $muestra" >&2
        echo "Un patron que ya no detecta deja esta comprobacion en verde para" >&2
        echo "siempre, que es peor que no tenerla." >&2
        exit 1
    fi
done

echo "  el patron reconoce las dos formas de la direccion"

# --- 2. El patron no marca lo que no es -------------------------------------
# La plantilla versionada despliegue.tex.example SI lleva una direccion, con
# XXXXXXXXXX en lugar del identificador. No se excluye por ruta a proposito:
# no lleva identificador alguno, luego no hay nada que tapar, y una exclusion
# por ruta dejaria ciega la comprobacion el dia que alguien pegue el valor real
# dentro de la plantilla, que si esta versionada.
for inocua in \
    "${esquema}${servicio}-XXXXXXXXXX.us-central1.run.app" \
    "${esquema}karisma-api-xyz.a.run.app" \
    "${esquema}servicio-1.a.run.app" \
    "${esquema}karisma-api-ejemplo.a.run.app" \
    "${esquema}${servicio}-\${GCP_PROJECT_NUMBER}.us-central1.run.app"; do
    if printf '%s\n' "$inocua" | grep -qE "$PATRON"; then
        echo "FALLA: el patron marca una direccion que no lleva identificador." >&2
        echo "Muestra marcada de mas: $inocua" >&2
        echo "Con falsos positivos, la siguiente persona anade una excepcion o" >&2
        echo "borra la comprobacion. Estrecha el patron, no la lista." >&2
        exit 1
    fi
done

echo "  el patron no marca marcadores de posicion ni nombres ficticios"

# --- 3. Nada versionado la contiene -----------------------------------------
# El listado es "--cached --others --exclude-standard": lo versionado MAS lo
# que esta sin versionar y sin ignorar. Con "git ls-files" a secas la barrera
# tenia un hueco del tamano de esta misma US, donde siete de los archivos
# nuevos siguen sin anadirse al indice: un .tex recien creado con la direccion
# dentro no lo miraba nadie hasta despues del commit. Lo ignorado queda fuera,
# que es donde viven a proposito datos/despliegue.tex y docs/entregables/tmp/.
# Los -z / -0 son obligatorios porque hay archivos con espacios en el nombre.
# "grep -I" salta los binarios, que es lo que deja fuera los PDF de las entregas.
HALLAZGOS=$(cd "$RAIZ" && git ls-files -z --cached --others --exclude-standard \
    | xargs -0 grep -InE "$PATRON" 2>/dev/null \
    | sed -E 's#(-[A-Za-z0-9]{8,}-[a-z]{2,3}\.a\.run\.app|-[0-9]{9,}\.)#-REDACTADO.#g' \
    || true)

if [ -n "$HALLAZGOS" ]; then
    echo ""
    echo "FALLA: un archivo que el repositorio va a publicar lleva la direccion." >&2
    echo "$HALLAZGOS" >&2
    echo "" >&2
    printf '%s\n' 'La direccion entra al documento por la macro \urlDemoWeb de' >&2
    echo "docs/entregables/datos/demo.tex; su valor lo escribe" >&2
    echo "'bash scripts/escribir_url_demo.sh' en datos/despliegue.tex, que git" >&2
    echo "ignora. En prosa fuera del entregable, citala por variable." >&2
    exit 1
fi

echo "  ningun archivo de texto por publicar la contiene"
echo ""
echo "En verde: la direccion del demo sigue fuera del repositorio publico."
