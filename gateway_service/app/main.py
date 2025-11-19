# Config
# Middleware
# Shared response
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# Routers
from gateway_service.app.api.v1.routes import auth, roles, user
from gateway_service.app.core.config import settings
from gateway_service.app.middleware.audit import AuditMiddleware
from gateway_service.app.middleware.auth import AuthMiddleware
from gateway_service.app.middleware.tracing import TraceMiddleware

app = FastAPI(
    title="Gateway Service",
    version="1.0.0",
    description="API Gateway for User, Auth, and Tenant microservices",
)

# -----------------------------
# Middleware
# -----------------------------
app.add_middleware(TraceMiddleware)
app.add_middleware(AuthMiddleware)
app.add_middleware(AuditMiddleware)
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
app.include_router(auth.router)
app.include_router(user.router)
app.include_router(roles.router)

# app.include_router(tenant.router)


# -----------------------------
# Root Endpoint
# -----------------------------
@app.get("/")
async def root():
    return {
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
        "status": "running",
    }


# -----------------------------
# Optional Health Check
# -----------------------------
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.SERVICE_NAME,
        "version": settings.SERVICE_VERSION,
    }


# -------------------------------------------------------------------
# 🔒 Custom OpenAPI schema for Bearer token authorization in Swagger
# -------------------------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="User Service",
        version="1.0.0",
        description="API for managing users, roles, and permissions.",
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
