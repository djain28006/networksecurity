# ---- Stage 1: Builder ----
FROM python:3.10-slim AS builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy only requirements first for caching
COPY requirements.txt .

# Install dependencies to a temporary directory
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

# ---- Stage 2: Final Image ----
FROM python:3.10-slim

WORKDIR /app

# Copy installed python libraries
COPY --from=builder /install /usr/local

# Copy project code (excluding everything in .dockerignore)
COPY . .

# Expose the Flask port
EXPOSE 8000

# Start the web app using Gunicorn
CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "2"]
