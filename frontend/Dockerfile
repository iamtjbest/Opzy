# Opzy frontend (Next.js 16, App Router). Uses `output: "standalone"` (next.config.ts)
# so the runtime image only carries the traced files, not the full node_modules tree.
#
# All the env vars this app reads at request time (API_URL, INTERNAL_API_SECRET,
# TRUSTED_PROXY_HOPS) are plain server-side process.env reads, not NEXT_PUBLIC_-prefixed,
# so they're supplied at container start, not baked in at build time.

FROM node:22-slim AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build


FROM node:22-slim AS runtime

WORKDIR /app
ENV NODE_ENV=production

# node:22-slim already ships a non-root "node" user at uid 1000 — reuse it instead of
# creating a new one, which fails with "UID 1000 is not unique" since that id is taken.
COPY --from=build --chown=node:node /app/.next/standalone ./
COPY --from=build --chown=node:node /app/.next/static ./.next/static
# No public/ directory exists yet (no static assets beyond what Next.js generates into
# .next/static). Add this line back if one gets added later:
#   COPY --from=build --chown=node:node /app/public ./public

USER node

EXPOSE 3000

# Render passes $PORT; the standalone server.js honors the PORT env var directly.
CMD ["sh", "-c", "HOSTNAME=0.0.0.0 PORT=${PORT:-3000} node server.js"]
