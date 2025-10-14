# Backend on latest CPython 3.13 (Debian slim)
FROM python:3.13-slim

# Build argument for environment
ARG ENVIRONMENT=dev

# Environment variables for safety and performance
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    ENVIRONMENT=${ENVIRONMENT}

# Working directory inside the container
WORKDIR /app

# Install essential build tools and certificates
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Upgrade pip toolchain (helps with newer Python wheels)
RUN python -m pip install --upgrade pip setuptools wheel

# Copy and install Python dependencies first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend source code
COPY . .

# Create a symlink to make "backend.src" imports resolvable
# (maps /app/backend → /app)
RUN ln -s . /app/backend

# Add /app to Python path so src imports work anywhere
ENV PYTHONPATH=/app

# Create non-root user and group
RUN groupadd -r appgroup || true \
    && useradd -r -g appgroup -d /home/appuser appuser || true \
    && mkdir -p /home/appuser \
    && chown -R appuser:appgroup /app /home/appuser

# Switch to non-root user for security
USER appuser

# Expose FastAPI port
EXPOSE 8001

# Start FastAPI using uvicorn
CMD ["python", "-m", "uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
