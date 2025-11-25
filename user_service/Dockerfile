# ---------- Base Image ----------
FROM python:3.12-slim

# ---------- Set workdir ----------
WORKDIR /app

# ---------- Install system deps ----------
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# ---------- Copy dependency files ----------
COPY user_service/pyproject.toml user_service/uv.lock ./

# ---------- Install all project dependencies ----------
RUN pip install --upgrade pip \
    && pip install --no-cache-dir .

# ---------- Copy microservice code ----------
COPY user_service /app/user_service

# ---------- Copy shared libs ----------
COPY shared_service /app/shared_service

# ---------- Entrypoint ----------
COPY user_service/docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh

# ---------- Default command ----------
CMD ["./docker-entrypoint.sh"]
