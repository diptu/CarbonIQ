"""Configuration settings for the Ingestion microservice."""

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

    # Database
    DATABASE_URL: Optional[str] = None
    READ_REPLICA_URL: Optional[str] = None

    # Pagination
    DEFAULT_PAGE_LIMIT: int = 10

    # File config
    MAX_FILE_SIZE: int = 10  # in MB
    UPLOAD_DIR: str = "uploads"  # from .env, initially a string

    # Redis config
    UPSTASH_REDIS_REST_URL: str = None
    UPSTASH_REDIS_REST_TOKEN: str = None

    # Pydantic v2 config
    model_config = SettingsConfigDict(env_file=str(ENV_FILE), extra="ignore")


settings = Settings()

# ---- Convert UPLOAD_DIR (str) → Path and ensure it exists ----
upload_path = (BASE_DIR / settings.UPLOAD_DIR).resolve()
if not upload_path.exists():
    upload_path.mkdir(parents=True)
settings.UPLOAD_DIR = upload_path
# -------------------------------------------------------------------
print(f"DATABASE_URL:{settings.DATABASE_URL}")

# Require DB on startup
if not settings.DATABASE_URL:
    raise ValueError("DATABASE_URL must be set in environment variables")
