# app/core/config.py
"""Application configuration settings for the IMA Service.

Centralized configuration for database, JWT, Redis, CORS, and audit logging.

Notes
-----
- Loads from environment variables and optional `.env` file.
- Cached via functools.lru_cache for efficiency.
- Supports JWT, Redis, audit logging, and multi-tenant defaults.
"""

from __future__ import annotations
from functools import lru_cache
from pathlib import Path
from typing import List, Optional, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # -----------------------------
    # Service
    # -----------------------------
    SERVICE_NAME: str = Field(default="ima_service", description="Service name for logging/metrics")
    SERVICE_VERSION: str = Field(default="1.0.0", description="Service version for logs/tracing")

    # -----------------------------
    # Database
    # -----------------------------
    DATABASE_URL: str = Field(..., description="Database connection URL")

    # -----------------------------
    # Application secrets
    # -----------------------------
    SECRET_KEY: str = Field(..., description="JWT signing secret key")
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    # -----------------------------
    # JWT / Authentication
    # -----------------------------
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15, description="Access token lifetime in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(default=7, description="Refresh token lifetime in days")
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_ISSUER: str = Field(default="ima_service", description="JWT issuer")
    JWT_AUDIENCE: str = Field(default="ima_clients", description="JWT audience")
    JWT_REFRESH_ROTATION_ENABLED: bool = Field(
        default=False, description="Enable refresh token rotation on use"
    )

    # -----------------------------
    # Redis
    # -----------------------------
    REDIS_URL: Optional[str] = Field(
        default=None, description="Redis URL for caching or token blacklisting"
    )
    REDIS_TOKEN: Optional[str] = Field(default=None, description="Redis connection token")
    REDIS_MAX_CONNECTIONS: int = Field(default=10, description="Max Redis connections in pool")

    # -----------------------------
    # Token cleanup
    # -----------------------------
    TOKEN_CLEANUP_ON_SHUTDOWN: bool = Field(
        default=True, description="Whether to cleanup expired/revoked tokens on shutdown"
    )
    TOKEN_CLEANUP_REVOKED_RETENTION_DAYS: int = Field(
        default=30, description="Number of days to retain revoked tokens before deletion"
    )
    TOKEN_CLEANUP_ACCESS_TOKENS: bool = Field(
        default=False, description="Whether to also cleanup expired access tokens on shutdown"
    )

    # -----------------------------
    # CORS
    # -----------------------------
    BACKEND_CORS_ORIGINS: Union[List[str], str] = Field(
        default_factory=lambda: ["http://localhost", "http://localhost:3000"],
        description="Allowed CORS origins",
    )

    # -----------------------------
    # Audit log
    # -----------------------------
    AUDIT_LOG_PATH: str = Field(
        default=str(BASE_DIR / "logs" / "audit.log"), description="Audit log file path"
    )

    # -----------------------------
    # Pydantic v2 settings
    # -----------------------------
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # -----------------------------
    # Validators
    # -----------------------------
    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            # support comma or semicolon separation
            return [o.strip() for o in v.replace(";", ",").split(",") if o.strip()]
        elif isinstance(v, list):
            return v
        raise ValueError("Invalid format for BACKEND_CORS_ORIGINS")


# -----------------------------
# Cached settings
# -----------------------------
@lru_cache
def get_settings() -> Settings:
    """Return cached Settings instance."""
    return Settings()  # type: ignore[call-arg]
