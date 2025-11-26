from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from gateway_service.app.core.config import settings
from shared_service.app.middleware.request_context import RequestContextMiddleware
from user_service.app.db.session import engine

from auth_service.app.api import auth_router

# Routers
from auth_service.app.models.token_blacklist import Base

app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description="API Service for Auth  microservices",
)

# -------------------------
# Middlewere
# -------------------------
app.add_middleware(RequestContextMiddleware)


# -----------------------------
# Root Endpoint
# -----------------------------

SERVER_HEALTH_DOCS = {
    "summary": "Server health",
    "description": "Check API server liveness.",
    "responses": {
        status.HTTP_200_OK: {"description": "Server is healthy"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Server health check failed"},
    },
}


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


# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# Routers
# -----------------------------
app.include_router(auth_router)


# -------------------------
# Create tables on startup
# -------------------------
@app.on_event("startup")
async def create_tables():
    """Create all database tables asynchronously on app startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


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
