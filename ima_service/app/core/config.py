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
from typing import List, Optional
from datetime import timedelta

from pydantic_settings import BaseSettings, SettingsConfigDict

# --- base directory and env file -----------------------------------
BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
ENV_FILE: Path = BASE_DIR / ".env"


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

    # --- convenience properties -----------------------------------------
    @property
    def access_token_expires(self) -> timedelta:
        """Return access token expiry as timedelta."""
        return timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)

    @property
    def refresh_token_expires(self) -> timedelta:
        """Return refresh token expiry as timedelta."""
        return timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)

    @property
    def cors_origins(self) -> List[str]:
        """Return BACKEND_CORS_ORIGINS parsed as a list of origins.

        Accepts comma-separated string values and trims whitespace.
        """
        raw: str = self.BACKEND_CORS_ORIGINS or ""
        if not raw:
            return []
        return [s.strip() for s in raw.split(",") if s.strip()]

    @property
    def audit_log_path(self) -> Path:
        """Return the audit log path as a pathlib.Path object."""
        return Path(self.AUDIT_LOG_PATH).expanduser().resolve()


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings loaded from the environment.

    Returns
    -------
    Settings
        Cached settings instance.
    """
    return Settings()  # type: ignore[call-arg]
