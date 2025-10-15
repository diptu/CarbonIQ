"""
Authentication endpoint documentation.
"""

LOGIN = {
    "summary": "Authenticate user and obtain tokens",
    "description": """Authenticate a user using email and password.

**What you need to provide**:
- Email address
- Password

**What you get**:
- Access token (short-lived)
- Refresh token (long-lived)
- Token type and expiry

**Errors**:
- 401 Unauthorized if credentials are invalid or user is inactive.

**Example request**:

POST /auth/login
```json
{
    "email": "jane.doe@example.com",
    "password": "SecurePass123"
}
```""",
}

REFRESH_TOKEN = {
    "summary": "Refresh access token using a refresh token",
    "description": """Exchange a valid refresh token for a new access token.

**What you need to provide**:
- Refresh token

**What you get**:
- New access token
- New refresh token
- Token type and expiry

**Errors**:
- 400 Bad Request if refresh token is invalid.

**Example request**:

POST /auth/refresh
```json
{
    "refreshToken": "existing-refresh-token"
}
```""",
}

LOGOUT = {
    "summary": "Logout user",
    "description": """Logout a user from the system.

**Notes**:
- Placeholder endpoint.
- Implement token revocation/blacklisting if needed for security.

**Example request**:

POST /auth/logout
No request body needed.
```""",
}
