from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = BASE_DIR / ".env"


class Settings(BaseSettings):
    SERVICE_NAME: str = "auth_service"
    SERVICE_VERSION: str = "0.0.1"
    APP_NAME: str | None = None
    APP_ENV: str | None = None
    DEBUG: bool = False

    USER_SERVICE_URL: str = "http://localhost:8000"
    AUTH_SERVICE_URL: str
    TENANT_SERVICE_URL: str
    AUDIT_SERVICE_URL: str

    # # Security
    SECRET_KEY: Optional[str] = None
    ALGORITHM: str = "HS256"

    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost", "http://localhost:3000"]

    class Config:
        env_file = str(ENV_FILE)
        env_file_encoding = "utf-8"


settings = Settings()
