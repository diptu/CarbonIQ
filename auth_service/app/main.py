from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# Routers
from gateway_service.app.core.config import settings
from shared_service.app.middleware.request_context import RequestContextMiddleware

from auth_service.app.api import auth_router

app = FastAPI(
    title="Auth Service",
    version="1.0.0",
    description="API Service for Auth  microservices",
)

# -----------------------------
# Middleware
# -----------------------------
# app.add_middleware(TraceMiddleware)
# app.add_middleware(AuthMiddleware)
# app.add_middleware(AuditMiddleware)
app.add_middleware(RequestContextMiddleware)
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
# Root Endpoint
# -----------------------------
@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "ok",
    }


# -----------------------------
# Routers
# -----------------------------
app.include_router(auth_router)


# -------------------------------------------------------------------
# 🔒 Custom OpenAPI schema for Bearer token authorization in Swagger
# -------------------------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Auth Service",
        version="1.0.0",
        description="Authentication microservice handling JWT generation, validation, \
            token revocation, and secure login workflows.",
        routes=app.routes,
    )

    # Add a simple BearerAuth scheme
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
            continue  # no auth needed for login/verify
        for method in methods.values():
            method.setdefault("security", [{"BearerAuth": []}])

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi
