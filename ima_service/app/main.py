# app/main.py
"""Main FastAPI application entrypoint for IMA Service."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.routes import router as api_v1_router
from app.core.config import get_settings

settings = get_settings()

# -------------------------
# Create FastAPI app
# -------------------------
app = FastAPI(
    title="IMA Service",
    description="API for User, Role, and Auth management",
    version="1.0.0",
)

# -------------------------
# CORS middleware
# -------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        origin.strip() for origin in settings.BACKEND_CORS_ORIGINS.split(",")
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------
# Include API routers
# -------------------------
app.include_router(api_v1_router, prefix="/api/v1")


# -------------------------
# Root endpoint
# -------------------------
@app.get("/", tags=["root"])
async def root():
    return {"message": "Welcome to IMA Service API"}


# -------------------------
# Startup / Shutdown events
# -------------------------
@app.on_event("startup")
async def startup_event():
    """
    Actions to run on startup.
    Pre-seed system roles if they do not exist.
    """
    from app.db.session import async_session
    from app.schemas.role import RoleName, RoleCreate
    from app.crud.role import get_role_by_name, create_role

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
