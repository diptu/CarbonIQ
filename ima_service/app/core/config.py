# app/core/config.py
"""Application configuration settings using Pydantic.

Pandas-style docstring
----------------------
This module defines the `Settings` class, which loads configuration
from environment variables and `.env` files. It centralizes database,
JWT, Redis, and audit-log settings.

Notes
-----
- Settings are cached via functools.lru_cache to avoid reloading.
- Compatible with mypy and pylint.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables.

    Attributes
    ----------
    DATABASE_URL : str
        SQLAlchemy database connection string.
    SECRET_KEY : str
        Secret key for cryptographic signing.
    DEBUG : bool
        Enable debug mode if True.
    ACCESS_TOKEN_EXPIRE_MINUTES : int
        Access token expiry time in minutes.
    REFRESH_TOKEN_EXPIRE_DAYS : int
        Refresh token expiry time in days.
    JWT_ALGORITHM : str
        Algorithm used for JWT signing/verification.
    JWT_ISSUER : str
        Expected JWT issuer claim.
    JWT_AUDIENCE : str
        Expected JWT audience claim.
    BACKEND_CORS_ORIGINS : str
        Comma-separated list of allowed CORS origins.
    REDIS_URL : Optional[str]
        Redis connection URL (if not set, in-memory cache is used).
    AUDIT_LOG_PATH : str
        Path to JSONL file for audit logs.
    """

    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool = False

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "ima_service"
    JWT_AUDIENCE: str = "ima_clients"
    BACKEND_CORS_ORIGINS: str = "http://localhost,http://localhost:3000"

    REDIS_URL: Optional[str] = None
    AUDIT_LOG_PATH: str = str(BASE_DIR / "logs" / "audit.log")

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings loaded from the environment.

    Returns
    -------
    Settings
        Cached settings instance.
    """
    return Settings()  # type: ignore[call-arg]
