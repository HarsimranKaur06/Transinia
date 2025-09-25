# Frontend Dockerfile - multi-stage build for Next.js production

# Stage 1: builder
FROM node:20-bullseye-slim AS builder
WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --silent

# Allow passing NEXT_PUBLIC_* envs at build time so Next.js can bake them into the build
ARG NEXT_PUBLIC_BACKEND_URL
ENV NEXT_PUBLIC_BACKEND_URL=${NEXT_PUBLIC_BACKEND_URL}

# Copy source and build
COPY . .
RUN npm run build

# Stage 2: runtime
FROM node:20-bullseye-slim AS runner
WORKDIR /app
ENV NODE_ENV=production

# Copy built assets and package.json for production deps

# Install only production dependencies

EXPOSE 3000
ENV PORT=3000

# NEXT_PUBLIC_* env vars are baked at build time; to change backend URL you must rebuild
# Use `--` so npm passes remaining args to the script (expects "start": "next start")
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

RUN npm ci --production --silent

CMD ["npm", "run", "start", "--", "-p", "${PORT}"]
