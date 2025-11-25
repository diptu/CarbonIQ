"""Configuration settings for the User microservice."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """App settings loaded from environment variables."""

    # General App Config
    SERVICE_NAME: str = "Auth Service"
    SERVICE_VERSION: str = "0.0.1"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # # Security
    # SECRET_KEY: Optional[str] = None
    # ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: Optional[str] = None
    READ_REPLICA_URL: Optional[str] = None

    # Pagination
    DEFAULT_PAGE_LIMIT: int = 10

    # Pydantic v2 config
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), extra="ignore")


# Instantiate settings
settings = Settings()

# Runtime validation for required fields

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")
