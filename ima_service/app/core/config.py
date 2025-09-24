# app/core/config.py
"""Application configuration settings using Pydantic."""

from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BASE_DIR = Path(__file__).resolve().parent.parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    """Application configuration loaded from environment variables."""

    DATABASE_URL: str
    DEBUG: bool = False
    SECRET_KEY: str

    model_config = SettingsConfigDict(
        env_file=str(ENV_FILE),
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings loaded from the environment."""
    return Settings()  # type: ignore[call-arg]
