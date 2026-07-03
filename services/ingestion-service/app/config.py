"""Centralized service configuration, loaded from environment variables."""

from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Service identity
    service_name: str = "ingestion-service"
    api_v1_prefix: str = "/api/v1"
    port: int = 8004
    environment: str = "local"

    # Database (PostgreSQL, per README's Microservices Catalog)
    database_url: str = (
        "postgresql+asyncpg://carboniq:carboniq@localhost:5432/ingestion"
    )
    database_echo: bool = False

    # Object storage (S3-compatible; MinIO locally, per deployments/docker-compose.yml)
    s3_endpoint_url: str | None = "http://localhost:9000"
    s3_bucket: str = "carboniq-ingestion"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"
    s3_region: str = "ap-southeast-2"
    s3_use_ssl: bool = False

    # Celery (RabbitMQ broker + Redis result backend, per the documented stack)
    celery_broker_url: str = "amqp://guest:guest@localhost:5672//"
    celery_result_backend: str = "redis://localhost:6379/0"
    celery_task_always_eager: bool = False
    """When true, tasks run synchronously in-process (useful for tests/dev without a broker)."""

    # Auth: JWTs are issued by auth-service (RS256) and validated here (zero-trust).
    # In production this is the auth-service's public signing key (JWKS/PEM). A shared
    # HS256 secret is supported for local dev to avoid needing a real key pair.
    jwt_algorithm: str = "RS256"
    jwt_public_key: str | None = None
    jwt_hs256_secret: str | None = "local-dev-shared-secret"
    jwt_issuer: str = "auth.service.local"
    jwt_audience: str | None = None

    # Downstream services this service dispatches ingested files to
    ocr_service_url: str = "http://localhost:8005"
    dispatch_timeout_seconds: float = 10.0

    # Upload constraints
    max_upload_size_bytes: int = 25 * 1024 * 1024  # 25 MB

    @field_validator("s3_endpoint_url", "jwt_public_key", "jwt_audience", mode="before")
    @classmethod
    def _blank_env_value_as_none(cls, value: object) -> object:
        """An empty `KEY=` line in .env means "unset", not the literal empty
        string — without this, `jwt_audience=""` would wrongly turn on
        audience verification for tokens that were never issued one."""
        if isinstance(value, str) and value.strip() == "":
            return None
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
