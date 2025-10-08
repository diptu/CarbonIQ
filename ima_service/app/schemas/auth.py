from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field


class TokenDetails(BaseModel):
    accessToken: str
    refreshToken: str
    tokenType: str = "bearer"
    expiresIn: int
    roles: List[str] = []
    tenantId: Optional[str] = None


class LoginResponse(BaseModel):
    statusCode: int
    msg: str
    details: TokenDetails


class TokenRefresh(BaseModel):
    refreshToken: str
