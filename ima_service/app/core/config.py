"""Application configuration settings for the IMA Service.

Pandas-style docstring
----------------------
Centralized configuration for database, JWT, Redis, CORS, and audit logging.

Notes
-----
- Loads from environment variables and optional `.env` file.
- Cached via functools.lru_cache for efficiency.
- Supports JWT, Redis, audit logging, and multi-tenant defaults.
- Type-checked and PEP8-compliant.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import List, Optional

from pydantic import Field, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


# Base project directory
BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application settings loaded from environment variables.

    Attributes
    ----------
    DATABASE_URL : str
        SQLAlchemy/PostgreSQL connection URL.
    SECRET_KEY : str
        Cryptographic secret key used for JWT signing.
    DEBUG : bool
        Enable debug mode.
    ACCESS_TOKEN_EXPIRE_MINUTES : int
        JWT access token expiry in minutes.
    REFRESH_TOKEN_EXPIRE_DAYS : int
        JWT refresh token expiry in days.
    JWT_ALGORITHM : str
        JWT signing algorithm (HS256/RS256).
    JWT_ISSUER : str
        Expected JWT issuer claim.
    JWT_AUDIENCE : str
        Expected JWT audience claim.
    BACKEND_CORS_ORIGINS : List[str]
        Allowed CORS origins.
    REDIS_URL : Optional[str]
        Redis connection URL for caching or token revocation.
    AUDIT_LOG_PATH : str
        Path for storing audit logs (JSONL format).
    """

    DATABASE_URL: str = Field(..., description="Database connection URL")
    SECRET_KEY: str = Field(..., description="JWT signing secret key")
    DEBUG: bool = Field(default=False, description="Enable debug mode")

    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(
        default=15, description="Access token lifetime in minutes"
    )
    REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=7, description="Refresh token lifetime in days"
    )
    JWT_ALGORITHM: str = Field(default="HS256", description="JWT signing algorithm")
    JWT_ISSUER: str = Field(default="ima_service", description="JWT issuer")
    JWT_AUDIENCE: str = Field(default="ima_clients", description="JWT audience")
    BACKEND_CORS_ORIGINS: List[str] = Field(
        default_factory=lambda: ["http://localhost", "http://localhost:3000"],
        description="Allowed CORS origins",
    )

    REDIS_URL: Optional[str] = Field(
        default=None, description="Redis URL for caching or token blacklisting"
    )
    AUDIT_LOG_PATH: str = Field(
        default=str(BASE_DIR / "logs" / "audit.log"), description="Audit log file path"
    )

    # Pydantic v2 config
    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )

    # --- Validators ---
    @validator("BACKEND_CORS_ORIGINS", pre=True)
    @classmethod
    def parse_cors_origins(cls, v):
        """Convert comma-separated string to list if needed."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v


@lru_cache
def get_settings() -> Settings:
    """Return cached settings instance.

    Returns
    -------
    Settings
        Loaded and cached configuration for the application.
    """
    return Settings()  # type: ignore[call-arg]
