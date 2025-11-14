"""Configuration settings for the User microservice."""

from pathlib import Path
from typing import Optional
from uuid import UUID

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """App settings loaded from environment variables."""

    # General App Config
    APP_NAME: str = "multi_tenant_saas"
    APP_ENV: str = "development"
    USER_SERVICE_URL: str = "http://user-service:8000/users"
    DEBUG: bool = True
    BASE_DOMAIN: str = "carboniq.com"
    SYSTEM_USER_ID: UUID = "ecf72c1d-a729-4812-9e35-7f3dec625b09"

    # Database
    DATABASE_URL: Optional[str] = None

    # Pydantic v2 config
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), extra="ignore")


# Instantiate settings
settings = Settings()

# Runtime validation for required fields

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")
