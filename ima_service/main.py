# ima_service/main.py
"""FastAPI application entrypoint (minimal)."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import AsyncIterator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import (
    configure_logging,
    get_logger,
    get_settings,
    register_exception_handlers,
)
from app.api.v1.routes import router as api_v1_router
from app.core import __version__ as core_version
from app.persistence import configure_engine, init_db

log = get_logger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    st = get_settings()
    configure_logging(st)
    configure_engine(st)
    if getattr(st, "debug", False):
        init_db()
    log.info("app started", extra={"env": st.env, "version": core_version})
    yield
    log.info("app stopped")


def create_app() -> FastAPI:
    st = get_settings()
    app = FastAPI(
        title=st.app_name,
        version=core_version,
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    if getattr(st, "cors_origins", []):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=st.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    register_exception_handlers(app)
    app.include_router(api_v1_router, prefix="/api/v1")

    @app.get("/")
    async def root() -> dict[str, str]:
        return {"status": "ok", "version": core_version}

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run("ima_service.main:app", host="0.0.0.0", port=8000, reload=True)
