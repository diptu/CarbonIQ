# ruff: noqa: D100
# pylint: disable=too-few-public-methods
"""Tiny settings with .env + legacy env support."""

from __future__ import annotations

import os
from enum import Enum
from functools import lru_cache

from pydantic import BaseModel, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    """DB SETTINGS"""

    url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ima"
    pool_size: int = 10
    max_overflow: int = 20


class JWTSettings(BaseModel):
    """JWT SETTINGS"""

    secret_key: SecretStr = SecretStr("change-me")
    algorithm: str = "HS256"
    access_expire_minutes: int = 15
    refresh_expire_days: int = 7


class LogLevel(str, Enum):
    """Log Level SETTINGS"""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"


class LoggingSettings(BaseModel):
    """Log SETTINGS"""

    level: LogLevel = LogLevel.INFO
    color: bool = True
    json_file: str | None = None


class RedisSettings(BaseModel):
    """Redis SETTINGS"""

    host: str = "localhost"
    port: int = 6379
    password: SecretStr | None = None
    db: int = 0
    ssl: bool = False


class Settings(BaseSettings):
    """Core SETTINGS"""

    model_config = SettingsConfigDict(
        env_prefix="IMA_",
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "IMA Service"
    env: str = "dev"
    cors_origins: list[str] = []

    db: DatabaseSettings = DatabaseSettings()
    jwt: JWTSettings = JWTSettings()
    log: LoggingSettings = LoggingSettings()
    redis: RedisSettings | None = None

    @property
    def debug(self) -> bool:
        """dev-only SQL echo"""
        return self.env.lower() == "dev"


def _g(k: str, envv: dict[str, str], filev: dict[str, str]) -> str | None:
    """Get a key from real env or .env dict (env wins)."""
    return envv.get(k) or filev.get(k)


def _parse_env(path: str) -> dict[str, str]:
    """Very small .env reader: KEY=VALUE, ignores comments/quotes."""
    out: dict[str, str] = {}
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for ln in fh:
                s = ln.strip()
                if not s or s.startswith("#") or "=" not in s:
                    continue
                k, v = s.split("=", 1)
                out[k.strip()] = v.strip().strip('"').strip("'")
    except FileNotFoundError:
        pass
    return out


def _truthy(v: str | None) -> bool:
    """Coerce typical truthy strings to bool."""
    return str(v).lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Env loader with optional legacy var assembly."""
    env_file = os.getenv("IMA_ENV_FILE", ".env")
    filev = _parse_env(env_file)
    envv = dict(os.environ)

    s = Settings(_env_file=env_file)  # type: ignore[call-arg]

    # ---- DB URL: direct DSN or assemble from parts
    dsn = _g("IMA_DB__URL", envv, filev) or _g("IMA_DB_URL", envv, filev)
    if not dsn:
        db = {
            "user": _g("IMA_DB__USER", envv, filev)
            or _g("IMA_DB_USER", envv, filev)
            or "postgres",
            "password": _g("IMA_DB__PASSWORD", envv, filev)
            or _g("IMA_DB_PASSWORD", envv, filev)
            or "postgres",
            "host": _g("IMA_DB__HOST", envv, filev)
            or _g("IMA_DB_HOST", envv, filev)
            or "localhost",
            "port": _g("IMA_DB__PORT", envv, filev)
            or _g("IMA_DB_PORT", envv, filev)
            or "5432",
            "name": _g("IMA_DB__NAME", envv, filev)
            or _g("IMA_DB_NAME", envv, filev)
            or "ima",
            "driver": _g("IMA_DB__DRIVER", envv, filev)
            or _g("IMA_DB_DRIVER", envv, filev)
            or "psycopg",
        }
        db_ssl_str = _g("IMA_DB__SSL_MODE", envv, filev) or _g(
            "IMA_DB_SSL_MODE", envv, filev
        )
        dsn = (
            f"postgresql+{db['driver']}://{db['user']}:{db['password']}"
            f"@{db['host']}:{db['port']}/{db['name']}"
        )
        if db_ssl_str:
            dsn += f"?sslmode={db_ssl_str}"
    s.db.url = dsn  # type: ignore[assignment]

    # ---- Redis: create only when host exists
    if s.redis is None:
        rhost = _g("IMA_REDIS__HOST", envv, filev) or _g("IMA_REDIS_HOST", envv, filev)
        if rhost:
            s.redis = RedisSettings(
                host=rhost,
                port=int(
                    _g("IMA_REDIS__PORT", envv, filev)
                    or _g("IMA_REDIS_PORT", envv, filev)
                    or "6379"
                ),
                password=(
                    SecretStr(pw)
                    if (
                        pw := _g("IMA_REDIS__PASSWORD", envv, filev)
                        or _g("IMA_REDIS_PASSWORD", envv, filev)
                    )
                    else None
                ),
                db=int(
                    _g("IMA_REDIS__DB", envv, filev)
                    or _g("IMA_REDIS_DB", envv, filev)
                    or "0"
                ),
                ssl=_truthy(
                    _g("IMA_REDIS__SSL", envv, filev)
                    or _g("IMA_REDIS_SSL", envv, filev)
                ),
            )
    return s
