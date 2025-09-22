# Python 3.11 slim, no cache, non-root, production-ready
FROM python:3.11-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Minimal OS deps (add libpq/ca-certificates if needed)
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    ca-certificates curl && rm -rf /var/lib/apt/lists/*

# Non-root user
RUN useradd -m -u 10001 app
WORKDIR /app/ima_service

# Copy service source (compose uses build.context: .. so this path exists)
COPY ima_service /app/ima_service

# Install service (PEP 517 build from pyproject.toml)
RUN pip install --upgrade pip && pip install --no-cache-dir .

# Runtime
USER app
EXPOSE 8000
CMD ["uvicorn","main:app","--host","0.0.0.0","--port","8000"]
