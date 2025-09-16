# Use lightweight Python 3.13 image
FROM python:3.13-slim

# Set working directory inside container
WORKDIR /app

# Copy dependencies first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Environment variables
ENV PYTHONUNBUFFERED=1

# Expose FastAPI port
EXPOSE 8001

# Default: run FastAPI (so frontend can talk to it)
ENTRYPOINT ["python", "-m", "uvicorn", "backend.src.api:app"]
CMD ["--host", "0.0.0.0", "--port", "8001", "--workers", "1"]
