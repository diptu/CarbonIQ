# app/api/v1/routes/auth_router.py
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.user_service import authenticate_user, create_tokens_for_user

router = APIRouter()


@router.post("/login")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    OAuth2 password login endpoint.
    Returns access & refresh tokens.
    """
    tenant_id = form_data.client_id or None
    user = await authenticate_user(
        db, form_data.username, form_data.password, tenant_id
    )

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    roles = [r.name for r in user.roles]
    tokens = create_tokens_for_user(user, roles)

    return tokens
