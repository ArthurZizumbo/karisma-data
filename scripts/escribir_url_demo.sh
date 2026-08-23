#!/usr/bin/env bash
# ===========================================================================
# Karisma Data - Escribe docs/entregables/datos/despliegue.tex (US-AVANCE-5)
#
# La direccion publica del demo entra al entregable por variable: el
# repositorio es publico y una URL de Cloud Run lleva dentro el identificador
# del proyecto de GCP. La mitad versionada del contrato es datos/demo.tex;
# este guion produce la otra mitad, que .gitignore excluye.
#
# Uso:
#   bash scripts/escribir_url_demo.sh              # pregunta a gcloud
#   URL_WEB=https://... bash scripts/escribir_url_demo.sh   # valor explicito
# ===========================================================================
set -euo pipefail

PROYECTO="${PROYECTO:-tareas-computo-nube}"
REGION="${REGION:-us-central1}"
RAIZ="$(cd "$(dirname "$0")/.." && pwd)"
DESTINO="$RAIZ/docs/entregables/datos/despliegue.tex"

URL_WEB="${URL_WEB:-$(gcloud run services describe karisma-web \
  --region="$REGION" --project="$PROYECTO" \
  --format="value(status.url)" 2>/dev/null || true)}"

if [ -z "$URL_WEB" ]; then
  printf '\033[1;31m[FALLO]\033[0m %s\n' \
    "No se obtuvo la URL de karisma-web. Autentica gcloud o pasala en URL_WEB." >&2
  exit 1
fi

# El caracter de porcentaje comenta el resto de la linea en TeX y una URL de
# Cloud Run no lo lleva, pero una direccion pegada a mano si podria: se escapa
# antes de escribir para que el documento no pierda media linea en silencio.
URL_TEX="${URL_WEB//%/\%}"

cat > "$DESTINO" <<TEX
%% Generado por scripts/escribir_url_demo.sh - no se versiona.
%% El contrato de macros vive en datos/demo.tex.
\renewcommand{\urlDemoWebValor}{$URL_TEX}
TEX

printf '\033[1;32m[OK]\033[0m %s\n' "datos/despliegue.tex escrito con $URL_WEB"
