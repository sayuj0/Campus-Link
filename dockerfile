FROM python:3.12.8-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.12.8-slim

LABEL maintainer="your-team@company.com" \
      version="1.0.0"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app/src \
    FLASK_ENV=production \
    PORT=8000 \
    WORKERS=2 \
    THREADS=2 \
    TIMEOUT=60 \
    PATH=/home/appuser/.local/bin:$PATH

WORKDIR /app

# Create non-root user early
RUN useradd -m -u 1000 appuser && \
    mkdir -p instance && \
    chown -R appuser:appuser /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/appuser/.local

# Copy application code with correct ownership
COPY --chown=appuser:appuser . .

# Switch to non-root user
USER appuser

EXPOSE 8000


# Run Gunicorn with configurable workers - now with startup message
CMD ["sh", "-c", "echo 'Access the server at http://localhost:8000/' && gunicorn -b 0.0.0.0:${PORT} app:app -w ${WORKERS} --threads ${THREADS} --timeout ${TIMEOUT} --access-logfile - --error-logfile -"]