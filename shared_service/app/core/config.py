"""Configuration settings for the shared microservice."""

from pathlib import Path
from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """App settings loaded from environment variables."""

    # General App Config
    APP_NAME: str = "carboniq"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Security
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    TENANT_REQUEST_TIMEOUT_SECONDS: int = 90
    USER_SERVICE_URL: Optional[str] = None
    AUTH_SERVICE_URL: Optional[str] = None
    AUDIT_SERVICE_URL: Optional[str] = None
    TENANT_SERVICE_URL: Optional[str] = None

    AUTH_ISSUER: str = "auth.carboniq.com"
    AUTH_AUDIENCE: str = "api.carboniq.com"

    # Pydantic v2 config
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), extra="ignore")


# Instantiate settings
settings = Settings()

# Runtime validation for required fields
if not settings.SECRET_KEY:
    raise ValueError("SECRET_KEY must be set in environment variables")
