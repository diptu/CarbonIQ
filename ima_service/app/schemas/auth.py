"""
Schemas for authentication and token management.
Includes login, token issuance, refresh, and standardized API response envelope.
"""

from pydantic import BaseModel
from .base import ORMBase, APIResponse


# ----------------------
# Token schema
# ----------------------
class Token(ORMBase):
    """Response schema for issued JWT tokens."""

    accessToken: str
    refreshToken: str
    tokenType: str
    expiresIn: int


# ----------------------
# Token refresh request
# ----------------------
class TokenRefresh(ORMBase):
    """Request schema for refreshing an access token."""

    refreshToken: str


# ----------------------
# Login request schema
# ----------------------
class LoginRequest(ORMBase):
    """Request schema for user login credentials."""

    email: str
    password: str


# ----------------------
# Concrete API response for login
# ----------------------
class LoginAPIResponse(APIResponse):
    details: Token
