"""FastAPI application entrypoint.

Run locally with:

    uv run uvicorn app.main:app --reload --port 8004
"""

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import api_router
from app.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.storage.s3 import get_object_storage

logging.basicConfig(level=logging.INFO)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    try:
        get_object_storage().ensure_bucket()
    except Exception:
        logging.getLogger("ingestion_service").warning(
            "Could not reach object storage at startup — uploads will fail until it's available",
            exc_info=True,
        )
    yield


app = FastAPI(
    title="CarbonIQ Ingestion Service",
    description=(
        "Handles file upload and validation (PDF/image bills, NEM12 smart-meter "
        "CSVs, REC/LGC certificates, PPA contracts), then dispatches to the "
        "appropriate downstream service."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

register_exception_handlers(app)
app.include_router(api_router, prefix=settings.api_v1_prefix)
