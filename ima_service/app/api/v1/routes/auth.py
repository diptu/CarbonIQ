from typing import List, Tuple, Optional
from fastapi import APIRouter, Form, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from uuid import UUID

from app.api.deps import get_db
from app.crud.user_basic import get_user_by_email
from app.utils.security import verify_password
from app.utils.jwt_utils import create_access_token, create_refresh_token
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/auth", tags=["auth"])


async def get_user_roles_with_tenant(
    db: AsyncSession, user_id: str
) -> List[Tuple[str, Optional[str]]]:
    """Return list of (role_name, tenant_id) for a given user."""
    result = await db.execute(
        text("""
            SELECT r.name, ur.tenant_id
            FROM roles r
            JOIN user_roles ur ON ur.role_id = r.id
            WHERE ur.user_id = :user_id
        """),
        {"user_id": user_id},
    )
    rows = result.fetchall()
    # Convert UUIDs to strings for JSON safety
    return [(row[0], str(row[1]) if row[1] else None) for row in rows]


@router.post("/login")
async def login(
    email: str = Form(..., description="Your email address"),
    password: str = Form(..., description="Your password"),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return JWT access + refresh tokens.
    Includes tenant_id in token claims.
    """
    # 1. Get user
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not getattr(user, "is_active", True):
        raise HTTPException(status_code=401, detail="User inactive")

    # 2. Get roles + tenant_id
    roles_with_tenant = await get_user_roles_with_tenant(db, str(user.id))
    if not roles_with_tenant:
        raise HTTPException(
            status_code=403, detail="Cannot determine tenant from your credentials"
        )

    roles: List[str] = [r[0] for r in roles_with_tenant]
    tenant_id = roles_with_tenant[0][1]  # pick the first tenant_id

    # 3. Create tokens (UUIDs converted to str)
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "type": "access",
            "role": roles,
            "tenant_id": tenant_id,
        }
    )
    refresh_token = create_refresh_token(
        data={
            "sub": str(user.id),
            "type": "refresh",
            "role": roles,
            "tenant_id": tenant_id,
        }
    )

    # 4. Return response
    return {
        "statusCode": 200,
        "msg": "Login successful",
        "details": {
            "accessToken": access_token,
            "refreshToken": refresh_token,
            "tokenType": "bearer",
            "expiresIn": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "roles": roles,
            "tenantId": tenant_id,
        },
    }
