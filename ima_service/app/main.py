# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from app.db.session import engine
from app.db.base_class import Base
from app.api import api_router
from app.core.config import get_settings

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
# Include API router
# ----------------------
app.include_router(api_router, prefix="/api/v1")


# ----------------------
# Root endpoint
# ----------------------
@app.get("/", summary="Health check")
def root():
    return {"status": "ok", "service": "IMA Service"}


# ----------------------
# Startup event: create tables
# ----------------------
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


# ----------------------
# Custom OpenAPI for Swagger OAuth2
# ----------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title, version=app.version, routes=app.routes
    )

    # OAuth2 password flow
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "oauth2",
            "flows": {"password": {"tokenUrl": "/api/v1/auth/login", "scopes": {}}},
        }
    }

    # Apply globally to all endpoints (lock endpoints before auth)
    for path in openapi_schema.get("paths", {}).values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
