"""Schemas for authentication-related requests and responses."""

from pydantic import BaseModel


class Token(BaseModel):
    """Response schema for access and refresh tokens."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Data stored inside a JWT token."""
    user_id: str
    exp: int


class LoginRequest(BaseModel):
    """Request schema for user login."""
    email: str
    password: str


class RefreshRequest(BaseModel):
    """Request schema for refreshing an access token."""
    refresh_token: str
