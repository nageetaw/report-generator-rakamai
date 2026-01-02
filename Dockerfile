FROM python:3.11-slim

# 1. Environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/home/myuser/.local/bin:$PATH"

WORKDIR /app


# 2. Install System Deps (Postgres support)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*


# 3. Security: Create user and the unified storage directory
RUN useradd -m myuser && \
    mkdir -p /app/audio /app/reports  && \
    chown -R myuser:myuser /app


# 4. Install Python Dependencies
COPY --chown=myuser:myuser requirements.txt .
USER myuser
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir --user -r requirements.txt


# 5. Copy Application Code
COPY --chown=myuser:myuser . .


# 6. Internal Healthcheck (The image checks itself)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Ensure scripts are executable
RUN chmod +x ./start.sh ./start-dev.sh

EXPOSE 8000

# Default to Production start
CMD ["./start.sh"]
