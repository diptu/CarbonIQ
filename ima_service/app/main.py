"""Main FastAPI application entrypoint for IMA Service."""

from fastapi import FastAPI

from ima_service.app.api.v1.routes import router as api_v1_router
from ima_service.app.core.config import get_settings
from ima_service.app.crud.role import (  # pylint: disable=C0415
    create_role,
    get_role_by_name,
)
from ima_service.app.db.session import async_session  # pylint: disable=C0415
from ima_service.app.schemas.role import (  # pylint: disable=C0415
    RoleCreate,
    RoleName,
)

settings = get_settings()

# -------------------------
# Create FastAPI app
# -------------------------
app = FastAPI(
    title="IMA Service",
    description=(
        "IMA Service: API for managing Users, Roles, and Authentication.\n\n"
        "- Supports JWT-based authentication.\n"
        "- Standardized API responses.\n"
        "- Multi-tenant ready with RBAC support."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# -------------------------
# Include API routers
# -------------------------
app.include_router(api_v1_router, prefix="/api/v1")


# -------------------------
# Startup / Shutdown events
# -------------------------
@app.on_event("startup")
async def startup_event() -> None:
    """
    Actions to run on startup.
    Pre-seed system roles if they do not exist.
    """

    async with async_session() as db:
        for role_name in RoleName:
            existing = await get_role_by_name(db, role_name)
            if not existing:
                await create_role(
                    db,
                    role_in=RoleCreate(
                        name=role_name,
                        description=f"System role: {role_name}",
                        is_system=True,
                    ),
                )
