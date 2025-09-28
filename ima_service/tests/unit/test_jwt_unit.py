# tests/test_jwt_unit.py
import pytest
from ima_service.app.utils import token as token_utils
from datetime import datetime, timedelta, timezone
import jwt


def test_create_access_token_returns_string():
    payload = {"sub": "123", "type": "access"}
    access_token = token_utils.create_access_token(payload, expires_delta=60)
    assert isinstance(access_token, str)
    decoded = jwt.decode(
        access_token, token_utils.settings.SECRET_KEY, algorithms=["HS256"]
    )
    assert decoded["sub"] == "123"
    assert decoded["type"] == "access"


def test_create_refresh_token_returns_string():
    payload = {"sub": "456"}
    refresh_token = token_utils.create_refresh_token(payload, expires_delta=120)
    assert isinstance(refresh_token, str)
    decoded = jwt.decode(
        refresh_token, token_utils.settings.SECRET_KEY, algorithms=["HS256"]
    )
    assert decoded["sub"] == "456"
    assert decoded["type"] == "refresh"


def test_decode_token_raises_on_invalid_token():
    with pytest.raises(jwt.InvalidTokenError):
        token_utils.decode_token("invalid.token.string")
