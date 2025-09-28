# app/core/config.py
"""Application configuration settings using Pydantic."""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"

# Ensure .env is loaded
if ENV_FILE.exists():
    from dotenv import load_dotenv

    load_dotenv(dotenv_path=ENV_FILE)


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    DATABASE_URL: str
    SECRET_KEY: str
    DEBUG: bool = False

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    JWT_ALGORITHM: str = "HS256"
    JWT_ISSUER: str = "ima_service"
    JWT_AUDIENCE: str = "ima_clients"
    BACKEND_CORS_ORIGINS: str = "http://localhost,http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings loaded from the environment."""
    return Settings()
