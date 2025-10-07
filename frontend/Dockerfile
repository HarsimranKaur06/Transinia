# ---- Builder ----
FROM node:20-alpine AS builder
WORKDIR /app

COPY package*.json ./
COPY tsconfig.json ./
COPY jsconfig.json ./
COPY next.config.js ./
RUN npm ci --silent

# Run npm audit to surface any production vulnerabilities in build logs (does not fail build)
RUN npm audit --production --json > /tmp/npm_audit.json || true

ARG NEXT_PUBLIC_BACKEND_URL
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL:-"http://localhost:8001"}
ENV NEXT_PUBLIC_API_URL=${NEXT_PUBLIC_API_URL:-${NEXT_PUBLIC_BACKEND_URL}}
ENV NEXT_TELEMETRY_DISABLED=1

# Copy source files
COPY . .

# Debug info
RUN echo "NEXT_PUBLIC_BACKEND_URL: $NEXT_PUBLIC_BACKEND_URL"
RUN echo "NEXT_PUBLIC_API_URL: $NEXT_PUBLIC_API_URL"

# Verify that the path alias configuration is in place
RUN cat tsconfig.json
RUN cat next.config.js

# Run Next.js build with standard output
RUN npm run build

# ---- Runner (distroless, non-root) ----
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV=production NEXT_TELEMETRY_DISABLED=1 PORT=3000

# Create a non-root user to run the app (Alpine version)
RUN addgroup -S appgroup && adduser -S appuser -G appgroup -h /home/appuser && mkdir -p /home/appuser

# Copy standalone build output produced by Next
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

# Simplify the startup - no scripts needed
RUN chown -R appuser:appgroup /app

EXPOSE 3000

# Create a script to patch server.js before running it
RUN echo '#!/bin/sh' > /app/start.sh && \
    echo '# Patch server.js to force hostname binding to 0.0.0.0' >> /app/start.sh && \
    echo 'sed -i "s/server.listen(port, hostname)/server.listen(port, \"0.0.0.0\")/" /app/server.js' >> /app/start.sh && \
    echo 'sed -i "s/await app.prepare()/await app.prepare(); console.log(\"Next.js server binding to 0.0.0.0:\"+port)/" /app/server.js' >> /app/start.sh && \
    echo 'echo "Server file patched to force 0.0.0.0 binding"' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Start the server' >> /app/start.sh && \
    echo 'ls -la /app' >> /app/start.sh && \
    echo 'echo "ENV VARS:"' >> /app/start.sh && \
    echo 'env | sort' >> /app/start.sh && \
    echo 'echo "Starting server on 0.0.0.0:3000..."' >> /app/start.sh && \
    echo 'exec node server.js' >> /app/start.sh && \
    chmod +x /app/start.sh && \
    chown appuser:appgroup /app/start.sh

USER appuser
CMD ["/app/start.sh"]
