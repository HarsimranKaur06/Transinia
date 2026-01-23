# ------------------------------------------------------------
# FRONTEND — Next.js standalone runner for ECS Fargate (dev)
# Using multi-stage build for smaller, faster deploys
# ------------------------------------------------------------

# ---------- BUILDER STAGE ----------
FROM node:20.9.0-bookworm-slim AS builder

# Set working directory
WORKDIR /app

# Copy manifest and config files first (better caching)
COPY package*.json ./
COPY tsconfig.json ./
COPY jsconfig.json ./
COPY next.config.js ./

# Install dependencies silently for speed
RUN npm ci --silent

# Optional: capture production vulnerabilities (for logs only)
RUN npm audit --production --json > /tmp/npm_audit.json || true

# Build-time args (will be passed from GitHub workflow)
ARG NEXT_PUBLIC_BACKEND_URL
ARG NEXT_PUBLIC_API_URL

# Public environment variables for Next.js static optimization
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL:-"http://localhost:8001"} \
    NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-${NEXT_PUBLIC_BACKEND_URL}} \
    NEXT_TELEMETRY_DISABLED=1

# Copy all app source files
COPY . .

# Debug print — helps confirm environment baked at build time
RUN echo "NEXT_PUBLIC_BACKEND_URL: $NEXT_PUBLIC_BACKEND_URL" && \
    echo "NEXT_PUBLIC_API_URL: $NEXT_PUBLIC_API_URL" && \
    echo "NODE_ENV (build): $NODE_ENV" && \
    ls -la /app

# Build optimized Next.js standalone bundle
RUN npm run build

# ---------- RUNNER STAGE ----------
FROM node:20.9.0-bookworm-slim AS runner

# Working directory inside container
WORKDIR /app

# Install curl for ECS health checks
RUN apt-get update && apt-get install -y --no-install-recommends curl \
 && rm -rf /var/lib/apt/lists/*

# Environment setup for runtime
ENV NODE_ENV=production \
    NEXT_TELEMETRY_DISABLED=1 \
    PORT=3000 \
    HOST=0.0.0.0 \
    HOSTNAME=0.0.0.0

# Create non-root user and group for security
RUN groupadd -r appgroup || true \
    && useradd -r -g appgroup -d /home/appuser appuser || true \
    && mkdir -p /home/appuser \
    && chown appuser:appgroup /home/appuser

# Copy only required build output from builder
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Ensure correct permissions
RUN chown -R appuser:appgroup /app

# Expose port used by ECS + ALB
EXPOSE 3000

# Startup script for clarity and debug logs
RUN printf '%s\n' \
  '#!/bin/sh' \
  'set -eu' \
  'echo "--------------------------------------------------------"' \
  'echo "Starting Next.js standalone on $HOST:$PORT (production)"' \
  'echo "Environment: NODE_ENV=$NODE_ENV"' \
  'echo "--------------------------------------------------------"' \
  'ls -la /app || true' \
  'exec node server.js' \
  > /app/start.sh && chmod +x /app/start.sh && chown appuser:appgroup /app/start.sh

# Switch to non-root user
USER appuser

# Start application
CMD ["/app/start.sh"]
