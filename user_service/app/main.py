"""User service runner"""

from fastapi import FastAPI

from app.api.v1.routes import (
    permissoion_router,
    role_permission_router,
    role_router,
    user_permission_router,
    user_role_router,
    user_router,
)
from app.db.session import engine
from app.models.base import Base

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="User Service", version="1.0.0")

# Include routers
app.include_router(user_router)
app.include_router(role_router)
app.include_router(permissoion_router)
app.include_router(user_permission_router)
app.include_router(user_role_router)
app.include_router(role_permission_router)
