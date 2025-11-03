"""Configuration settings for the Auth microservice."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """App settings loaded from environment variables."""

    # General App Config
    APP_NAME: str = "multi_tenant_saas"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # # Security
    # SECRET_KEY: Optional[str] = None
    # ALGORITHM: str = "HS256"
    # ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    # REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    # USER_SERVICE_URL: str = "http://0.0.0.0:8000"
    # AUTH_ISSUER: str = "auth.carboniq.com"
    # AUTH_AUDIENCE: str = "api.carboniq.com"

    # Database
    DATABASE_URL: Optional[str] = None

    # Pydantic v2 config
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), extra="ignore")


# Instantiate settings
settings = Settings()

# Runtime validation for required fields

if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")
