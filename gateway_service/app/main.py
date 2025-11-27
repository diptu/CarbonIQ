# Config
# Middleware
# Shared response
from fastapi import FastAPI, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

# Routers
from gateway_service.app.api.v1.routes import auth, roles, user
from gateway_service.app.core.config import settings
from shared_service.app.middleware.request_context import RequestContextMiddleware

# -------------------------
# Initialize FastAPI app
# -------------------------
app = FastAPI(
    title="API Gateway Service",
    version="0.0.1",
    description="API responsible for tenant-aware user management, including user creation, role assignment, \
    permission definition, and retrieval of RBAC metadata. Designed to operate across isolated tenants in a \
    multi-tenant SaaS environment with strict access boundaries.",
)
app.add_middleware(RequestContextMiddleware)


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


# -------------------------------------------------------------------
# 🔒 Custom OpenAPI schema for Bearer token authorization in Swagger
# -------------------------------------------------------------------
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="API Gateway Service",
        version="0.0.1",
        description="API responsible for tenant-aware user management, including user creation, role assignment, \
    permission definition, and retrieval of RBAC metadata. Designed to operate across isolated tenants in a \
    multi-tenant SaaS environment with strict access boundaries.",
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
