"""User service runner"""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from app.api.v1.routes import user_router
from app.db.session import engine
from app.models.base import Base

# Create tables
Base.metadata.create_all(bind=engine)

# Initialize app
app = FastAPI(title="User Service", version="1.0.0")

# Include routers
app.include_router(user_router)
# app.include_router(role_router)
# app.include_router(permissoion_router)
# app.include_router(user_role_router)
# app.include_router(role_permission_router)
# app.include_router(user_permission_router)


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
