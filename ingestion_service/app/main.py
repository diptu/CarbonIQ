"""User service runner with async table creation and FastAPI initialization."""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from ingestion_service.app.api.v1.routes import upload_router
from ingestion_service.app.core.config import settings
from ingestion_service.app.db.init_db import import_all_models
from ingestion_service.app.db.session import engine
from ingestion_service.app.models.upload import Base
from shared_service.app.middleware.request_context import RequestContextMiddleware

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

app.include_router(upload_router)


# -------------------------
# Create tables on startup
# -------------------------
# @app.on_event("startup")
# async def create_tables():
#     """Create all database tables asynchronously on app startup."""
#     # Import all models before creating tables
#     import_all_models()
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


from sqlalchemy import text


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
