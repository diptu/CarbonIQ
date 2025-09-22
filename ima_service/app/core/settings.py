"""Settings: robust env parsing + JWT/Redis hardening (prod-ready, compact)."""

from __future__ import annotations
import json, os
from functools import lru_cache
from pydantic import BaseModel, Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseModel):
    url: str = "postgresql+psycopg://postgres:postgres@localhost:5432/ima"
    pool_size: int = 10
    max_overflow: int = 20


class JWTSettings(BaseModel):
    secret_key: SecretStr = SecretStr("change-me")
    algorithm: str = "HS256"
    access_expire_minutes: int = 15
    refresh_expire_days: int = 7
    issuer: str | None = None
    audience: str | None = None
    leeway_seconds: int = 60
    current_kid: str | None = None
    keys: dict[str, SecretStr] = {}


class LoggingSettings(BaseModel):
    level: str = "INFO"
    color: bool = True
    json_file: str | None = None


class RedisSettings(BaseModel):
    host: str = "localhost"
    port: int = 6379
    password: SecretStr | None = None
    db: int = 0
    ssl: bool = False


class Settings(BaseSettings):
    """Core config (env: IMA_*, nested via IMA_FOO__BAR)."""

    model_config = SettingsConfigDict(
        env_prefix="IMA_",
        env_file=".env",
        env_nested_delimiter="__",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "IMA Service"
    env: str = "dev"

    # Store raw value to avoid DotEnv provider failing on list[str]
    cors_origins_raw: str | list[str] | None = Field(default=None, alias="cors_origins")

    db: DatabaseSettings = DatabaseSettings()
    jwt: JWTSettings = JWTSettings()
    log: LoggingSettings = LoggingSettings()
    redis: RedisSettings | None = None

    # computed DSNs for Redis token store / rate limiting
    redis_dsn: SecretStr | None = None
    redis_url: SecretStr | None = None

    @property
    def debug(self) -> bool:  # extra logging in dev
        return self.env.lower() == "dev"

    @property
    def cors_origins(self) -> list[str]:
        """Normalized CORS origins from CSV or JSON list; empty if unset."""
        v = self.cors_origins_raw
        if v in (None, "", []):
            return []
        if isinstance(v, list):
            return [str(x).strip() for x in v if str(x).strip()]
        s = str(v).strip()
        if not s:
            return []
        # Try JSON first (["http://a", "http://b"])
        if s.startswith("["):
            try:
                arr = json.loads(s)
                if isinstance(arr, list):
                    return [str(x).strip() for x in arr if str(x).strip()]
            except Exception:
                pass
        # Fallback CSV
        return [t.strip() for t in s.split(",") if t.strip()]


def _g(k: str, envv: dict[str, str], filev: dict[str, str]) -> str | None:
    return envv.get(k) or filev.get(k)


def _parse_env(path: str) -> dict[str, str]:
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
    return str(v).lower() in {"1", "true", "yes", "on"}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    env_file = os.getenv("IMA_ENV_FILE", ".env")
    filev = _parse_env(env_file)
    envv = dict(os.environ)

    s = Settings(_env_file=env_file)  # type: ignore[call-arg]

    # --- DB URL (IMA_DB__URL or assemble)
    dsn = _g("IMA_DB__URL", envv, filev) or _g("IMA_DB_URL", envv, filev)
    if not dsn:
        user = (
            _g("IMA_DB__USER", envv, filev)
            or _g("IMA_DB_USER", envv, filev)
            or "postgres"
        )
        pw = (
            _g("IMA_DB__PASSWORD", envv, filev)
            or _g("IMA_DB_PASSWORD", envv, filev)
            or "postgres"
        )
        host = (
            _g("IMA_DB__HOST", envv, filev)
            or _g("IMA_DB_HOST", envv, filev)
            or "localhost"
        )
        port = (
            _g("IMA_DB__PORT", envv, filev) or _g("IMA_DB_PORT", envv, filev) or "5432"
        )
        name = (
            _g("IMA_DB__NAME", envv, filev) or _g("IMA_DB_NAME", envv, filev) or "ima"
        )
        driver = (
            _g("IMA_DB__DRIVER", envv, filev)
            or _g("IMA_DB_DRIVER", envv, filev)
            or "psycopg"
        )
        sslmode = _g("IMA_DB__SSL_MODE", envv, filev) or _g(
            "IMA_DB_SSL_MODE", envv, filev
        )
        dsn = f"postgresql+{driver}://{user}:{pw}@{host}:{port}/{name}"
        if sslmode:
            dsn += f"?sslmode={sslmode}"
    s.db.url = dsn  # type: ignore[assignment]

    # --- Redis structured config if host provided
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

    # --- Compute redis_dsn/url (explicit URL/DSN wins; else build from RedisSettings)
    direct = _g("IMA_REDIS_DSN", envv, filev) or _g("IMA_REDIS_URL", envv, filev)
    if direct:
        s.redis_dsn = SecretStr(direct)
        s.redis_url = SecretStr(direct)
    elif s.redis is not None:
        scheme = "rediss" if s.redis.ssl else "redis"
        auth = f":{s.redis.password.get_secret_value()}@" if s.redis.password else ""
        built = f"{scheme}://{auth}{s.redis.host}:{s.redis.port}/{s.redis.db}"
        s.redis_dsn = SecretStr(built)
        s.redis_url = SecretStr(built)

    return s


__all__ = [
    "Settings",
    "get_settings",
    "DatabaseSettings",
    "JWTSettings",
    "LoggingSettings",
    "RedisSettings",
]
