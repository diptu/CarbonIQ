import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, cast

from jose import ExpiredSignatureError, JWTError, jwt
from jose.exceptions import ExpiredSignatureError, JWTError

from shared_service.app.core.config import settings


def create_access_token(
    sub: str,
    iss: str = "auth.carboniq.com",
    aud: str = "api.carboniq.com",
    roles: Optional[List[str]] = None,
    permissions: Optional[List[str]] = None,
    tenant_id: Optional[str] = None,
    return_payload: bool = False,
) -> Any:
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    payload: Dict[str, Any] = {
        "sub": sub,
        "iss": iss,
        "aud": aud,
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4()),
        "type": "access",
        "roles": roles or [],
        "permissions": permissions or [],
        "tenant_id": tenant_id,
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return (token, payload) if return_payload else token


def create_refresh_token(
    sub: str,
    return_payload: bool = False,
) -> Any:
    expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {
        "sub": sub,
        "exp": expire,
        "iat": datetime.utcnow(),
        "jti": str(uuid.uuid4()),
        "type": "refresh",
    }

    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return (token, payload) if return_payload else token


def decode_token(
    token: str,
    secret_key: Optional[str] = None,
    algorithm: Optional[str] = None,
) -> Dict[str, Any]:
    secret_key = secret_key or settings.SECRET_KEY
    algorithm = algorithm or settings.ALGORITHM
    audience = settings.AUTH_AUDIENCE

    try:
        payload = jwt.decode(
            token, secret_key, algorithms=[algorithm], audience=audience
        )
        print("✅ JWT decoded successfully:", payload)
        return cast(Dict[str, Any], payload)
    except ExpiredSignatureError:
        print("❌ Token expired")
        raise
    except JWTError as exc:
        print("❌ JWT decode error:", exc)
        raise
