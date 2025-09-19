# -------- Stage 1: Builder --------
FROM python:3.11-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app/ima_service

# Install uv
RUN pip install --upgrade pip && pip install uv

# Copy lock + manifest first for better layer caching
COPY pyproject.toml uv.lock ./

# Install production dependencies into a local venv (.venv)
# --no-dev ensures we don't pull dev/test deps into the runtime image
RUN uv sync --no-dev --frozen

# -------- Stage 2: Runtime --------
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
     PYTHONUNBUFFERED=1 \
     PATH="/app/ima_service/.venv/bin:${PATH}" \
     PYTHONPATH="/app"

WORKDIR /app/ima_service

# keep the service as a top-level package inside /app
COPY . /app/ima_service

# Bring in the virtualenv from the builder stage
COPY --from=builder /app/ima_service/.venv /app/ima_service/.venv

EXPOSE 8000

# Health probes often check /api/v1/health; keep CMD simple here
CMD ["uvicorn", "ima_service.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
