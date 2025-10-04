# Python 3.11 slim, production-ready, non-root
FROM python:3.11-slim AS runtime

# Prevent .pyc files, output logs unbuffered, no pip cache
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Minimal OS deps (add libpq & ca-certificates for Postgres SSL)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    libpq-dev \
    ca-certificates \
    curl \
 && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 10001 app
WORKDIR /app

# Copy project source
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip \
 && pip install --no-cache-dir .

# Runtime
USER app
EXPOSE 8000

CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]
