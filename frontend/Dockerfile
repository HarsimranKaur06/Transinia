# ---- Builder ----
FROM node:20-bookworm-slim AS builder
WORKDIR /app

COPY package*.json ./
RUN npm ci --silent

# Run npm audit to surface any production vulnerabilities in build logs (does not fail build)
RUN npm audit --production --json > /tmp/npm_audit.json || true

ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}
ENV NEXT_TELEMETRY_DISABLED=1

COPY . .
RUN npm run build

# ---- Runner (distroless, non-root) ----
FROM node:20-bookworm-slim AS runner
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000

# Create a non-root user to run the app
RUN groupadd -r appgroup && useradd -r -g appgroup -d /home/appuser -s /sbin/nologin appuser && mkdir -p /home/appuser

# Copy standalone build output produced by Next
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

EXPOSE 3000
USER appuser
CMD ["node", "server.js"]
