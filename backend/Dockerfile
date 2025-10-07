# Backend on latest CPython 3.13 (Debian slim)
FROM python:3.13-slim

# Fast, safe defaults
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# ---- (optional but recommended) system deps for native wheels on 3.13 ----
# If your requirements include packages that need compilation (e.g. uvloop, httptools),
# these keep builds smooth on 3.13. If you don't need them, you can remove.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# Upgrade pip toolchain (helps with 3.13 wheels)
RUN python -m pip install --upgrade pip setuptools wheel

# ---- Python deps first for better layer caching ----
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ---- App code ----
COPY . .

# Expose FastAPI port
EXPOSE 8001

# If uvicorn[standard] pulls uvloop/httptools and they don’t yet have 3.13 wheels on your platform,
# the build step above allows them to compile. If you *still* hit issues, try forcing pure asyncio:
# ENV UVICORN_LOOP=asyncio UVICORN_HTTP=h11

# Start the API
# Create a comprehensive fix script for import issues
RUN echo '#!/bin/sh\n\n# Show environment information\necho "==== ENVIRONMENT VARIABLES ===="\nenv | sort\necho "==== PYTHON PATH CONTENTS ===="\nfind /app -name "*.py" | sort\necho "=============================="\n\n# Create symbolic link to make backend.src resolve to src\nmkdir -p /backend\nln -sf /app/src /backend/src\n\n# Execute command\nexec "$@"' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Set PYTHONPATH to include both app and root directory
ENV PYTHONPATH=/app:/

# Use the original API file but with the import path fixed by symlink
ENTRYPOINT ["/app/entrypoint.sh", "python", "-m", "uvicorn", "src.api:app"]
CMD ["--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
