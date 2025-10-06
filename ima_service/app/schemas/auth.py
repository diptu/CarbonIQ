"""Schemas for authentication and token management.

Tenant-aware and supports DB-driven RBAC.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field, EmailStr
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm


class TokenDetails(BaseModel):
    accessToken: str = Field(..., description="JWT access token")
    refreshToken: str = Field(..., description="JWT refresh token")
    tokenType: str = Field(default="bearer", description="Token type")
    expiresIn: int = Field(..., description="Token expiration time in seconds")
    roles: List[str] = Field(..., description="List of user roles")
    tenantId: Optional[str] = Field(
        None, description="Tenant ID associated with the token"
    )


class LoginResponse(BaseModel):
    statusCode: int = Field(..., description="HTTP status code")
    msg: str = Field(..., description="Response message")
    details: TokenDetails = Field(..., description="Token details and related metadata")


class TokenRefresh(BaseModel):
    """
    Request schema for refreshing an access token.

    Attributes
    ----------
    refreshToken : str
        The refresh token to obtain a new access token.
    """

    refreshToken: str


class OAuth2PasswordRequestFormEmail:
    """
    Form for OAuth2 password login.
    Uses 'username' field for email.
    """

    def __init__(
        self,
        username: str = Form(...),
        password: str = Form(...),
        scope: str = Form(""),
    ):
        self.username = username
        self.password = password
        self.scope = scope


class APIResponse(BaseModel):
    """
    Standard API response envelope.

    Attributes
    ----------
    statusCode : int
        HTTP status code of the response.
    msg : str
        Short descriptive message.
    """

    statusCode: int
    msg: str


class LoginAPIResponse(APIResponse):
    """
    API response schema for login containing JWT tokens.

    Attributes
    ----------
    details : Token
        The JWT token information for the authenticated user.
    """

    details: TokenDetails
