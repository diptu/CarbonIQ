"""
app/schemas/auth.py

Schemas for authentication and token management.
Includes login, token issuance, refresh, and standardized API response envelope.
"""

from pydantic import BaseModel
from fastapi import Form
from fastapi.security import OAuth2PasswordRequestForm


# ----------------------
# Token schema
# ----------------------
class Token(BaseModel):
    """Response schema for issued JWT tokens."""

    accessToken: str
    refreshToken: str
    tokenType: str
    expiresIn: int


# ----------------------
# Token refresh request
# ----------------------
class TokenRefresh(BaseModel):
    """Request schema for refreshing an access token."""

    refreshToken: str


# ----------------------
# OAuth2 password form using email
# ----------------------
class OAuth2PasswordRequestFormEmail(OAuth2PasswordRequestForm):
    """
    Replacement for OAuth2PasswordRequestForm to use `email` instead of `username`
    in Swagger Authorize UI.

    Swagger will display editable fields for email and password.
    """

    def __init__(
        username: str = Form(
            ...,
            description="Your email address (use email instead of username)",
            example="demo@admin.com",
        ),
        password: str = Form(..., description="Your password", example="Hello123"),
        scope: str = Form(""),
        client_id: str | None = None,
        client_secret: str | None = None,
    ):
        super().__init__(
            username=username,  # internally stored as username
            password=password,
            scope=scope,
            client_id=client_id,
            client_secret=client_secret,
        )


# ----------------------
# API response envelope
# ----------------------
class APIResponse(BaseModel):
    statusCode: int
    msg: str


class LoginAPIResponse(APIResponse):
    """API response schema for login containing JWT tokens."""

    details: Token
