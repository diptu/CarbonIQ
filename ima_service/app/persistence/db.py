# ruff: noqa: D100
"""Database bootstrap: engine factory and session helpers."""

from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator, Optional
from urllib.parse import urlparse

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.core.logging import get_logger
from app.core.settings import Settings, get_settings

log = get_logger(__name__)
_ENGINE: Engine | None = None  # set by configure_engine()


def configure_engine(settings: Optional[Settings] = None) -> None:
    """Create and cache the global engine from settings."""
    global _ENGINE  # pylint: disable=global-statement
    st = settings or get_settings()

    url = st.db.url
    parsed = urlparse(url)
    masked = (
        f"{parsed.scheme}://{parsed.hostname}:{parsed.port}{parsed.path}"
        if parsed.hostname
        else parsed.scheme
    )
    log.info("configuring db engine", extra={"dsn_target": masked})

    _ENGINE = create_engine(
        url,
        pool_pre_ping=True,
        pool_size=st.db.pool_size,
        echo=st.debug,
    )


def get_engine() -> Engine:
    """Return the configured engine (configure if needed)."""
    if _ENGINE is None:
        configure_engine()
    return _ENGINE  # type: ignore[return-value]


def init_db() -> None:
    """Create tables for SQLModel models (dev/prototyping)."""
    SQLModel.metadata.create_all(get_engine())
    log.debug("db metadata created")


@contextmanager
def session_scope() -> Iterator[Session]:
    """Provide a transactional scope for scripts/CLI/jobs."""
    with Session(get_engine()) as s:
        try:
            yield s
            s.commit()
        except Exception:  # pylint: disable=broad-except
            s.rollback()
            log.exception("session rolled back due to error")
            raise


def get_session() -> Iterator[Session]:
    """Yield a session per-request (FastAPI dependency)."""
    with Session(get_engine()) as s:
        yield s
