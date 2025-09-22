"""SQLModel engine + session factory (prod-ready, compact)."""

from __future__ import annotations
from typing import Iterator, Optional
from sqlmodel import SQLModel, Session, create_engine
from ..core.settings import get_settings

_ENGINE = None  # type: Optional["Engine"]


def get_engine():
    global _ENGINE  # noqa: PLW0603
    if _ENGINE is None:
        st = get_settings()
        _ENGINE = create_engine(
            st.db.url,
            echo=st.debug,
            pool_size=st.db.pool_size,
            max_overflow=st.db.max_overflow,
            future=True,
        )
    return _ENGINE


def init_db(create_all: bool = False) -> None:
    """Initialize DB; create tables only for simple/dev setups (migrations preferred)."""
    if create_all:
        SQLModel.metadata.create_all(get_engine())


def get_session() -> Iterator[Session]:
    """FastAPI dependency: `Depends(get_session)` yields a DB session."""
    with Session(get_engine()) as sess:
        yield sess
