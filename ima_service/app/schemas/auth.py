"""Schemas for authentication and token management.

Tenant-aware and supports DB-driven RBAC.
"""

from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm

from pydantic import BaseModel, EmailStr
from fastapi import Form


class Token(BaseModel):
    """
    Response schema for issued JWT tokens.

    Attributes
    ----------
    accessToken : str
        JWT access token for the authenticated user.
    refreshToken : str
        JWT refresh token for renewing access tokens.
    tokenType : str
        Type of the token, usually "Bearer".
    expiresIn : int
        Token expiration time in seconds.
    user_id : UUID
        ID of the authenticated user.
    tenant_id : UUID
        Tenant ID of the authenticated user.
    roles : List[str]
        List of role names assigned to the user.
    """

    accessToken: str
    refreshToken: str
    tokenType: str
    expiresIn: int
    user_id: UUID
    tenant_id: UUID
    roles: List[str]


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

    details: Token
