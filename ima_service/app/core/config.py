# FILE: ima_service/app/core/config.py
"""
Application configuration (Pydantic v2).

- Single `.env` file; ENV_FILE overrides.
- Environment variables > file.
- Nested sections for database, redis, rate-limit.
- Import-safe; cached Settings via get_settings().
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Final

from pydantic import Field, computed_field
from pydantic_settings import BaseSettings, SettingsConfigDict


def _resolve_env_file() -> str:
    """Resolve ENV_FILE or best-effort common locations."""
    val = os.getenv("ENV_FILE")
    if val:
        return val

    here = Path(__file__).resolve()
    candidates = [
        Path(".env"),
        here.parents[2] / ".env",  # repo root (…/ima_service/.env up two)
        here.parents[1] / ".env",  # under ima_service/
    ]
    for p in candidates:
        try:
            if p.exists():
                return str(p)
        except OSError:
            # Permission or filesystem errors – skip this candidate
            continue
    return ".env"


_ENV_FILE: Final[str] = _resolve_env_file()


# -----------------------------
# Sections
# -----------------------------
class DatabaseSettings(BaseSettings):
    """Database configuration (SQLAlchemy async DSN)."""

    uri: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/ima",
        alias="DB_URI",
        description="Full SQLAlchemy async DSN.",
    )
    user: str = Field(default="postgres", alias="DB_USER")
    password: str = Field(default="postgres", alias="DB_PASSWORD")
    host: str = Field(default="localhost", alias="DB_HOST")
    port: int = Field(default=5432, alias="DB_PORT")
    name: str = Field(default="ima", alias="DB_NAME")

    pool_min: int = Field(default=10, alias="DB_POOL_MIN")
    pool_max: int = Field(default=50, alias="DB_POOL_MAX")
    ssl_mode: str = Field(default="require", alias="DB_SSL_MODE")

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE, extra="allow", case_sensitive=False
    )

    @computed_field
    def effective_uri(self) -> str:
        """Prefer `uri` if it looks complete; else build from parts."""
        if "://" in (self.uri or ""):
            return self.uri
        return (
            f"postgresql+asyncpg://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.name}"
        )


class RedisSettings(BaseSettings):
    """Redis cache configuration."""

    url: str | None = Field(default=None, alias="REDIS_URL")
    host: str = Field(default="127.0.0.1", alias="REDIS_HOST")
    port: int = Field(default=6379, alias="REDIS_PORT")
    password: str = Field(default="", alias="REDIS_PASSWORD")
    db: int = Field(default=0, alias="REDIS_DB")
    cache_ttl: int = Field(default=3600, alias="REDIS_CACHE_TTL")

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE, extra="allow", case_sensitive=False
    )

    @computed_field
    def effective_url(self) -> str:
        """Return redis:// URL consumable by redis.asyncio."""
        if self.url:
            return self.url
        auth = "" if not self.password else f":{self.password}@"
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"


class RateLimitSettings(BaseSettings):
    """Rate limiting settings (basic)."""

    count: int = Field(default=5, alias="RATE_LIMIT_COUNT")
    window: int = Field(default=60, alias="RATE_LIMIT_WINDOW")  # seconds

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE, extra="allow", case_sensitive=False
    )


class Settings(BaseSettings):
    """Top-level application settings."""

    app_name: str = Field(default="IMA Service", alias="APP_NAME")
    base_url: str = Field(default="http://127.0.0.1:8000", alias="BASE_URL")
    env: str = Field(default="development", alias="ENV")
    debug: bool = Field(default=False, alias="DEBUG")
    port: int = Field(default=8000, alias="PORT")
    workers: int = Field(default=1, alias="WORKERS")

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)
    rate_limit: RateLimitSettings = Field(default_factory=RateLimitSettings)

    model_config = SettingsConfigDict(
        env_file=_ENV_FILE, extra="allow", case_sensitive=False
    )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
