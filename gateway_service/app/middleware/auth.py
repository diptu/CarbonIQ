import jwt
from fastapi import HTTPException, Request, status
from gateway_service.app.core.config import settings
from shared_service.app.utils.jwt_utils import decode_token
from starlette.middleware.base import BaseHTTPMiddleware


class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                payload = decode_token(token, settings.SECRET_KEY, algorithms=settings.ALGORITHM)
                request.state.current_user = {
                    "user_id": payload.get("sub"),
                    "tenant_id": payload.get("tenant_id"),
                    "roles": payload.get("roles", []),
                    "permissions": payload.get("permissions", []),
                    "access_token": token,
                }
            except jwt.ExpiredSignatureError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
                )
            except jwt.InvalidTokenError:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
                )
        else:
            request.state.current_user = {}
        return await call_next(request)
