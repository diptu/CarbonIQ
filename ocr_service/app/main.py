"""User service runner with async table creation and FastAPI initialization."""

import asyncio

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from ingestion_service.app.api.v1.routes import ocr_router
from ingestion_service.app.core.config import settings
from ingestion_service.app.db.init_db import import_all_models
from ingestion_service.app.db.session import engine
from ingestion_service.app.models.upload import Base
from ocr_service.app.core.kafka import init_producer
from shared_service.app.middleware.request_context import RequestContextMiddleware
from sqlalchemy import text

from app.core.ocr_consumer import consume_raw_files_loop

# -------------------------
# Initialize FastAPI app
# -------------------------
app = FastAPI(
    title="User Service",
    version="1.0.0",
    description="API for creating and managing users, assigning roles, defining permissions, \
        and retrieving RBAC-related metadata used across the multi-tenant system.",
)
app.add_middleware(RequestContextMiddleware)
from fastapi import status

SERVER_HEALTH_DOCS = {
    "summary": "Server health",
    "description": "Check API server liveness.",
    "responses": {
        status.HTTP_200_OK: {"description": "Server is healthy"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Server health check failed"},
    },
}


# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/", **SERVER_HEALTH_DOCS)
async def root():
    async def server_check() -> bool:
        """
        Lightweight internal check.
        Replace/extend this with:
        - CPU/memory threshold checks
        - Internal service checks
        - Dependency readiness (cache, message broker, etc.)
        """
        return True  # Always true unless extended

    is_alive = await server_check()

    return {
        "status": status.HTTP_200_OK if is_alive else status.HTTP_500_INTERNAL_SERVER_ERROR,
        "server": "Server is healthy" if is_alive else "Server health check failed",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
    }


# -------------------------
# Include API routers
# -------------------------

app.include_router(ocr_router)


# -------------------------
# Create tables on startup
# -------------------------


@app.on_event("startup")
async def create_tables():
    """Create all database tables asynchronously on app startup."""
    import_all_models()  # Ensure all models are registered

    async with engine.begin() as conn:
        # Create tables
        await conn.run_sync(Base.metadata.create_all)

        # Debug: list tables from metadata
        print("Tables registered in Base.metadata:", list(Base.metadata.tables.keys()))

        # Debug: check actual tables in database
        result = await conn.run_sync(
            lambda sync_conn: sync_conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname='public';")
            ).fetchall()
        )
        print("Tables in database:", [row[0] for row in result])
        # start kafka producer (so publish works)
    try:
        await init_producer()
        print("[startup] Kafka producer initialized")
    except Exception as e:
        print("[startup] Kafka producer init failed:", e)

    # start consumer loop in background
    asyncio.create_task(consume_raw_files_loop())
    print("[startup] OCR consumer launched")


# -------------------------
#  on shutdown
# -------------------------


@app.on_event("shutdown")
async def shutdown():
    # aiokafka producer/consumer cleanup handled by modules
    print("[shutdown] service stopping")


# -------------------------
# Custom OpenAPI schema with BearerAuth
# -------------------------
def custom_openapi():
    """Add BearerAuth security scheme to all endpoints except login & verify."""
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    # Define Bearer token scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply BearerAuth to all endpoints except login & verify
    for path, methods in openapi_schema["paths"].items():
        if path.startswith("/auth") or path.startswith("/users/verify"):
            continue
        for method in methods.values():
            method.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
