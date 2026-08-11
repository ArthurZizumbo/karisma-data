# syntax=docker/dockerfile:1

# Multi-stage build for the Karisma Data API.
# Build context is backend/, which is what `gcloud run deploy karisma-api
# --source backend` and the `api` service of docker-compose.yml both use.

# Stage 1: turn the committed lock file into a plain requirements file.
# Poetry lives here and never reaches the runtime image.
FROM python:3.12-slim AS builder

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_NO_INTERACTION=1

WORKDIR /build

RUN pip install "poetry==2.2.1" "poetry-plugin-export==1.10.0"

COPY pyproject.toml poetry.lock ./
# Con hashes: la imagen de produccion verifica el contenido de cada paquete, no
# solo su version. Es la misma tesis que llevo a US-002 a anadir +sha512 al
# packageManager de pnpm, aplicada al arbol de Python.
RUN poetry export --format requirements.txt --output requirements.txt --only main

# Stage 2: runtime. Slim image with the pinned dependencies and the source only.
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=8000

# /app is the path assumed by the anonymous volume of docker-compose.yml.
WORKDIR /app

COPY --from=builder /build/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

RUN useradd --create-home --uid 1001 karisma
USER karisma

# Docker Compose publishes 8000; Cloud Run injects PORT=8080 at runtime.
EXPOSE 8000

# The image ships its own probe because python:3.12-slim has no curl or wget.
HEALTHCHECK --interval=10s --timeout=3s --start-period=15s --retries=5 \
    CMD python -c "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:' + os.environ.get('PORT', '8000') + '/health').read()" || exit 1

CMD ["sh", "-c", "exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT}"]
