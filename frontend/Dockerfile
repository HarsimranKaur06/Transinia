# ---- Builder ----
FROM node:20.9.0-bookworm-slim AS builder
WORKDIR /app

# Install deps
COPY package*.json ./
COPY tsconfig.json ./
COPY jsconfig.json ./
COPY next.config.js ./
RUN npm ci --silent

# Optional: surface prod vulns in logs (won't fail build)
RUN npm audit --production --json > /tmp/npm_audit.json || true

# Public runtime config (baked at build for static optimization only)
ARG NEXT_PUBLIC_BACKEND_URL
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL:-"http://localhost:8001"}
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-${NEXT_PUBLIC_BACKEND_URL}}
ENV NEXT_TELEMETRY_DISABLED=1

# App source
COPY . .

# Debug info
RUN echo "NEXT_PUBLIC_BACKEND_URL: $NEXT_PUBLIC_BACKEND_URL" && \
    echo "NEXT_PUBLIC_API_URL: $NEXT_PUBLIC_API_URL" && \
    cat tsconfig.json && \
    cat next.config.js

# Build Next.js (standalone output)
RUN npm run build

# ---- Runner ----
FROM node:20.9.0-bookworm-slim AS runner
WORKDIR /app

# Install curl for ECS health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Ensure production mode and explicit bind/port
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOST=0.0.0.0 \
    HOSTNAME=0.0.0.0

# Non-root user
RUN groupadd -r appgroup || true \
    && useradd -r -g appgroup -d /home/appuser appuser || true \
    && mkdir -p /home/appuser \
    && chown appuser:appgroup /home/appuser

# Copy standalone output
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Ownership
RUN chown -R appuser:appgroup /app

EXPOSE 3000

# Simple start script (no patching)
RUN printf '%s\n' \
  '#!/bin/sh' \
  'set -eu' \
  'echo "Starting Next.js (standalone) on $HOST:$PORT..."' \
  'echo "Env (filtered): NODE_ENV=$NODE_ENV PORT=$PORT HOST=$HOST HOSTNAME=$HOSTNAME"' \
  'ls -la /app || true' \
  'exec node server.js' > /app/start.sh \
  && chmod +x /app/start.sh \
  && chown appuser:appgroup /app/start.sh

USER appuser
CMD ["/app/start.sh"]
