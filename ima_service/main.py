"""FastAPI app factory for ima_service.

Use with:
  uvicorn ima_service.main:app --reload --port 8000
or (dev) python -m ima_service.main
"""

from __future__ import annotations

import logging
import sys
from typing import Optional

import uvicorn
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Import using package-qualified names so imports resolve whether running as:
# - `uvicorn ima_service.main:app` (recommended), or
# - `python -m ima_service.main`
from ima_service.app.api.openapi import build_openapi
from ima_service.app.api.v1.routes import router as api_v1_router
from ima_service.app.core.errors import AppError
from ima_service.app.core.logging import configure_logging
from ima_service.app.core.settings import Settings, get_settings

logger = logging.getLogger("ima.main")


def create_app(*, settings: Optional[Settings] = None) -> FastAPI:
    """Create and configure FastAPI app instance."""
    st = settings or get_settings()
    configure_logging()
    app = FastAPI(title=st.app_name, debug=st.debug, version="0.1.0")

    if st.cors_origins:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=st.cors_origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    @app.exception_handler(AppError)
    async def _app_error(_req: Request, exc: AppError) -> JSONResponse:
        # keep structured error body
        return JSONResponse(status_code=exc.status_code, content=exc.to_dict())

    # include v1 API
    app.include_router(api_v1_router)

    # custom OpenAPI generator (cached on app)
    def _custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        app.openapi_schema = build_openapi(app, st)
        return app.openapi_schema

    app.openapi = _custom_openapi  # type: ignore[assignment]
    logger.info("App created: %s (env=%s)", st.app_name, st.env)
    return app


# module-level WSGI/ASGI app — importable by uvicorn
app = create_app()


if __name__ == "__main__":  # pragma: no cover - developer convenience
    # Support running with `python -m ima_service.main` for dev convenience.
    cfg = get_settings()
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    logger.info("Starting dev server on port %d", port)
    uvicorn.run("ima_service.main:app", host="127.0.0.1", port=port, reload=cfg.debug)
