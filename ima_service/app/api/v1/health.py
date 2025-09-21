# ruff: noqa: D100
"""Health checks: server, db, redis, aggregate (compact, strict status)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Final

from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.core import __version__ as core_version
from app.core.logging import get_logger
from app.core.settings import get_settings
from app.persistence.db import get_engine

router = APIRouter(prefix="/health", tags=["health"])
log = get_logger(__name__)
_STARTED_AT = datetime.now(timezone.utc)

# -------------------- docs helpers -----------------------------------------


def _doc(summary: str, description: str, op_id: str) -> Dict[str, Any]:
    return {"summary": summary, "description": description, "operation_id": op_id}


SERVER_HEALTH_DOCS: Final = _doc("Server", "Is the API reachable?", "healthServer")
DATABASE_HEALTH_DOCS: Final = _doc("Database", "DB connectivity.", "healthDatabase")
REDIS_HEALTH_DOCS: Final = _doc("Redis", "Redis connectivity.", "healthRedis")
FULL_HEALTH_DOCS: Final = _doc("Aggregate", "Server + DB + Redis checks.", "healthFull")

# -------------------- envelopes --------------------------------------------


def _ok(
    *,
    message: str = "OK",
    data: Dict[str, Any] | None = None,
    meta: Dict[str, Any] | None = None,
    status_code: int = status.HTTP_200_OK,
) -> JSONResponse:
    body: Dict[str, Any] = {"status": "success", "message": message}
    if data is not None:
        body["data"] = data
    if meta is not None:
        body["meta"] = meta
    return JSONResponse(content=body, status_code=status_code)


def _fail(
    *,
    message: str,
    code: str = "ERROR",
    details: Dict[str, Any] | None = None,
    status_code: int = status.HTTP_400_BAD_REQUEST,
    status_text: str | None = None,
) -> JSONResponse:
    body: Dict[str, Any] = {
        "status": status_text or ("fail" if 400 <= status_code < 500 else "error"),
        "code": code,
        "message": message,
    }
    if details:
        body["details"] = details
    return JSONResponse(content=body, status_code=status_code)


# -------------------- helpers ----------------------------------------------


def _human(name: str, value: str) -> str:
    return {
        "ok": f"{name} is healthy",
        "degraded": f"{name} is degraded",
        "down": f"{name} is not healthy",
        "disabled": f"{name} check is disabled",
        "missing": f"{name} client is missing",
    }.get(value, f"{name} status: {value}")


def _server_obj() -> Dict[str, Any]:
    st = get_settings()
    now = datetime.now(timezone.utc)
    uptime = int((now - _STARTED_AT).total_seconds())
    return {
        "status": "ok",
        "message": _human("Server", "ok"),
        "app": st.app_name,
        "version": core_version,
        "env": str(st.env),
        "time": now.isoformat(),
        "uptime_seconds": uptime,
    }


def _db_status() -> str:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:  # pylint: disable=broad-except
        log.error("db health check failed: %s", exc)
        return "down"


def _redis_status() -> str:
    st = get_settings()
    cfg = getattr(st, "redis", None)
    if cfg is None:
        return "disabled"
    try:
        import redis  # lazy import

        client = redis.Redis(
            host=cfg.host,
            port=cfg.port,
            password=(cfg.password.get_secret_value() if cfg.password else None),
            db=cfg.db,
            ssl=bool(cfg.ssl),
            socket_timeout=2.0,
            socket_connect_timeout=2.0,
        )
        return "ok" if client.ping() else "down"
    except ModuleNotFoundError:
        log.warning("redis package not installed")
        return "missing"
    except Exception as exc:  # pylint: disable=broad-except
        log.error("redis health check failed: %s", exc)
        return "down"


def _compact(name: str, s: str) -> Dict[str, str]:
    return {"status": s, "message": _human(name, s)}


async def _aggregate() -> Dict[str, Any]:
    db = _db_status()
    rd = _redis_status()
    overall = "ok" if db == "ok" and rd in {"ok", "disabled"} else "degraded"
    return {
        "status": overall,
        "message": _human("Service", overall),
        "server": _server_obj(),
        "database": _compact("Database", db),
        "redis": _compact("Redis", rd),
    }


# -------------------- routes -------------------------------------------------


@router.get("/server", **SERVER_HEALTH_DOCS)
async def server_health() -> JSONResponse:
    data = _server_obj()
    return _ok(message=data["message"], data=data)


@router.get("/database", **DATABASE_HEALTH_DOCS)
async def database_health() -> JSONResponse:
    s = _db_status()
    det = _compact("Database", s)
    if s == "ok":
        return _ok(message=det["message"], data=det)
    return _fail(
        message=det["message"],
        code="DB_DOWN",
        details=det,
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        status_text="error",
    )


@router.get("/redis", **REDIS_HEALTH_DOCS)
async def redis_health() -> JSONResponse:
    s = _redis_status()
    det = _compact("Redis", s)
    if s in {"ok", "disabled"}:
        return _ok(message=det["message"], data=det)
    return _fail(
        message=det["message"],
        code="REDIS_DOWN",
        details=det,
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        status_text="error",
    )


@router.get("/", **FULL_HEALTH_DOCS)
@router.get("", include_in_schema=False)  # no-slash alias to avoid 307
async def full_health() -> JSONResponse:
    det = await _aggregate()
    if det["status"] == "ok":
        return _ok(message=det["message"], data=det)
    return _fail(
        message=det["message"],
        code="SERVICE_DEGRADED",
        details=det,
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        status_text="error",
    )
