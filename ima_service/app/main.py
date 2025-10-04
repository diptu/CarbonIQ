from typing import Any, Dict

from fastapi import FastAPI, Depends, Request, Security
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer

from ima_service.app.api.v1.routes import router as api_v1_router
from app.core.config import get_settings
from app.crud.role import create_role, get_role_by_name
from app.db.session import async_session
from app.schemas.role import RoleCreate, RoleName
from app.utils.token import decode_token

settings = get_settings()

app = FastAPI(
    title="IMA Service",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.include_router(api_v1_router, prefix="/api/v1")

# OAuth2 scheme for Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


# --------------------------
# Dependency: get current user
# --------------------------
async def get_current_user(token: str = Depends(oauth2_scheme)) -> str:
    try:
        payload = decode_token(token)
        if payload.get("type") != "access" or not payload.get("sub"):
            raise Exception("Invalid token")
        return payload["sub"]
    except Exception:
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )


@app.get("/me")
async def read_current_user(user_id: str = Depends(get_current_user)) -> Dict[str, Any]:
    return {"user_id": user_id}


# --------------------------
# Custom OpenAPI for Swagger
# --------------------------
def custom_openapi() -> Dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title, version=app.version, routes=app.routes
    )

    # Add OAuth2 Bearer
    openapi_schema.setdefault("components", {}).setdefault("securitySchemes", {})[
        "OAuth2PasswordBearer"
    ] = {
        "type": "http",
        "scheme": "bearer",
        "bearerFormat": "JWT",
        "description": "Use access token from /auth/login",
    }

    # Apply globally to all endpoints
    for path in openapi_schema.get("paths", {}).values():
        for method in path.values():
            method["security"] = [{"OAuth2PasswordBearer": []}]

    # Optional: fix login form schema in Swagger
    login_path = "/api/v1/auth/login"
    if login_path in openapi_schema.get("paths", {}):
        post = openapi_schema["paths"][login_path].get("post", {})
        request_schema = (
            post.get("requestBody", {})
            .get("content", {})
            .get("application/x-www-form-urlencoded", {})
            .get("schema", {})
        )
        if (
            "properties" in request_schema
            and "username" in request_schema["properties"]
        ):
            request_schema["properties"]["username"]["title"] = "email"
            request_schema["properties"]["username"]["description"] = "User email"

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# --------------------------
# Startup event: create system roles
# --------------------------
@app.on_event("startup")
async def startup_event() -> None:
    async with async_session() as db:
        for role_name in RoleName:
            existing = await get_role_by_name(db, role_name)
            if not existing:
                await create_role(
                    db,
                    RoleCreate(
                        name=role_name,
                        description=f"System role: {role_name}",
                        is_system=True,
                    ),
                )
