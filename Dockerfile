# Production Dockerfile for AutoPrice AI (MyDash Analytics)
FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8501

WORKDIR /app

# Install system dependencies if required
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files, pre-trained models, and pre-calculated analytics
COPY src/ /app/src/
COPY app/ /app/app/
COPY models/ /app/models/
COPY data/ /app/data/
COPY run_app.py /app/

# Expose server port
EXPOSE 8501

# Healthcheck
HEALTHCHECK CMD curl --fail http://localhost:8501/api/health || exit 1

# Launch production server
CMD ["sh", "-c", "uvicorn app.server:app --host 0.0.0.0 --port ${PORT:-8501}"]
