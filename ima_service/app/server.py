# app/server.py

"""
Entrypoint for IMA Service.
Sets up FastAPI, CORS, OpenAPI, and DB initialization.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.db.session import engine  # type: ignore
from app.db.base_class import Base  # type: ignore

# from app.api import api_router  # type: ignore
from app.core.config import get_settings  # type: ignore

settings = get_settings()

app = FastAPI(
    title="IMA Service - DB-driven RBAC",
    description="Tenant-aware Role-Based Access Control service",
    version="1.0.0",
)

# ----------------------
# CORS middleware
# ----------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ----------------------
# Include API router if exists
# ----------------------
# app.include_router(api_router, prefix="/api/v1")  # type: ignore


# ----------------------
# Root endpoint
# ----------------------
@app.get("/", summary="Health check")
async def root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok", "service": "IMA Service"}


# ----------------------
# Startup event: create tables
# ----------------------
@app.on_event("startup")
async def startup_event() -> None:
    """Create tables at startup (DEV only)."""
    if settings.DEBUG:
        async with engine.begin() as conn:  # type: ignore
            await conn.run_sync(Base.metadata.create_all)  # type: ignore


# ----------------------
# Custom OpenAPI with BearerAuth
# ----------------------
def custom_openapi() -> dict:
    """Generate OpenAPI schema with JWT Bearer."""
    if app.openapi_schema:
        return app.openapi_schema

    schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )

    schema["components"]["securitySchemes"] = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    # Apply security only to endpoints with dependencies
    for path_item in schema["paths"].values():
        for operation in path_item.values():
            if "dependencies" in operation:
                operation["security"] = [{"BearerAuth": []}]

    app.openapi_schema = schema
    return app.openapi_schema


app.openapi = custom_openapi  # type: ignore[method-assign]
