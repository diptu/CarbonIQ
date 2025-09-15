from __future__ import annotations

import os
from functools import lru_cache
from typing import Final

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_ENV_FILE: Final = os.getenv("ENV_FILE", ".env")


class DatabaseSettings(BaseSettings):
    uri: str = Field(..., alias="DB_URI")
    pool_min: int = Field(10, alias="DB_POOL_MIN")
    pool_max: int = Field(50, alias="DB_POOL_MAX")
    replica1_host: str | None = Field(None, alias="DB_REPLICA1_HOST")
    replica2_host: str | None = Field(None, alias="DB_REPLICA2_HOST")
    ssl_mode: str = Field("require", alias="DB_SSL_MODE")

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="allow")


class RedisSettings(BaseSettings):
    host: str = Field(..., alias="REDIS_HOST")
    port: int = Field(..., alias="REDIS_PORT")
    password: str = Field(..., alias="REDIS_PASSWORD")
    db: int = Field(..., alias="REDIS_DB")
    cache_ttl: int = Field(3600, alias="REDIS_CACHE_TTL")

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="allow")


class RateLimitSettings(BaseSettings):
    count: int = Field(5, alias="RATE_LIMIT_COUNT")
    window: int = Field(60, alias="RATE_LIMIT_WINDOW")

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="allow")


class Settings(BaseSettings):
    app_name: str = Field(..., alias="APP_NAME")
    base_url: str = Field(..., alias="BASE_URL")
    env: str = Field(..., alias="ENV")
    debug: bool = Field(..., alias="DEBUG")
    port: int = Field(..., alias="PORT")

    database: DatabaseSettings = Field(default_factory=DatabaseSettings)
    redis: RedisSettings = Field(default_factory=RedisSettings)

    model_config = SettingsConfigDict(env_file=_ENV_FILE, extra="allow")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
