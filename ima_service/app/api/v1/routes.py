# ima_service/app/api/v1/routes.py
from app.api.v1 import health
from app.api.v1 import users as users_module  # <-- no try/except
from app.core.logging import get_logger
from fastapi import APIRouter

router = APIRouter()
log = get_logger(__name__)

router.include_router(health.router)
router.include_router(users_module.router)  # -> /api/v1/users/...
