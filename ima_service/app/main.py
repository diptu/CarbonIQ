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

    # 1. Define the Bearer Token Security Scheme
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",  # Use the HTTP security scheme
            "scheme": "bearer",  # Specify the authentication scheme as 'bearer'
            "bearerFormat": "JWT",  # Optional: for documentation purposes
            "description": "JWT Authorization header using the Bearer scheme. Example: 'Authorization: Bearer {token}'",
        }
    }

    # 2. Apply Security Globally to All Endpoints (except the health check/root)
    # This automatically adds the padlock icon to all secured paths
    for path_item in openapi_schema.get("paths", {}).values():
        for operation in path_item.values():
            # Exclude the root health check or other public endpoints if needed
            if "security" not in operation:
                # Apply the security requirement
                operation["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
