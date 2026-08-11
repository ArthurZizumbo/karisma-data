# frontend/Dockerfile - Nuxt 4 SSR con capa de cache de pnpm fetch
FROM node:22-slim AS builder

# Valor por defecto de la base del API. Solo es el que queda horneado en
# runtimeConfig; el proxy de /api/** vive en server/api/[...].ts y relee
# runtimeConfig.apiBase en cada solicitud, asi que NUXT_API_BASE en tiempo de
# ARRANQUE gana sobre este ARG. Es lo que permite que la misma imagen sirva en
# Compose (http://api:8000) y en Cloud Run, donde la URL del backend solo se
# conoce despues de desplegarlo y "gcloud run deploy --source" no acepta
# argumentos de construccion.
ARG NUXT_API_BASE=http://api:8000
ENV NUXT_API_BASE=$NUXT_API_BASE

RUN corepack enable
WORKDIR /app

# Los bindings nativos (rolldown, unrs-resolver) son dependencias OPCIONALES:
# si su tarball falla al descargarse, pnpm lo omite en silencio y el error solo
# aparece despues, como "Cannot find native binding". Reintentos generosos para
# que una red lenta no produzca una imagen incompleta.
ENV npm_config_fetch_retries=5
ENV npm_config_fetch_retry_mintimeout=20000
ENV npm_config_fetch_retry_maxtimeout=120000
ENV npm_config_fetch_timeout=600000

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
RUN pnpm fetch

COPY . .
# --prefer-offline y no --offline: la capa anterior sigue sirviendo de cache,
# pero si a "pnpm fetch" le falto un binding opcional por un fallo de red, este
# paso lo recupera en vez de morir con la imagen a medias.
RUN pnpm install --frozen-lockfile --prefer-offline && pnpm build

FROM node:22-slim AS runtime

ENV NODE_ENV=production
ENV HOST=0.0.0.0
# Cloud Run inyecta PORT y sobreescribe este valor; Compose usa 3000.
ENV PORT=3000

WORKDIR /app
COPY --from=builder /app/.output ./.output

# El servicio expuesto a internet no corre como root. La imagen node:22-slim ya
# trae el usuario "node" (uid 1000), asi que no hace falta crearlo. El backend
# hace lo mismo con su propio uid 1001: la simetria es deliberada.
USER node

EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
