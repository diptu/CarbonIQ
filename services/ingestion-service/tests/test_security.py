"""Regression tests for JWT config/verification edge cases."""

import datetime
import uuid

import jwt as pyjwt

from app.config import Settings
from app.core.security import decode_token


def test_blank_env_values_normalize_to_none():
    """A bare `JWT_AUDIENCE=` line in .env yields "" from the environment,
    not None — Settings must normalize that, or verify_aud silently turns on
    for every token, rejecting all of them (see services/ingestion-service
    README's local-dev auth flow, which relies on tokens with no aud claim).
    """
    settings = Settings(jwt_audience="", jwt_public_key="", s3_endpoint_url="")
    assert settings.jwt_audience is None
    assert settings.jwt_public_key is None
    assert settings.s3_endpoint_url is None


def test_decode_token_accepts_hs256_token_without_audience_claim():
    settings = Settings(
        jwt_algorithm="HS256",
        jwt_hs256_secret="test-secret",
        jwt_issuer="auth.service.local",
        jwt_audience="",  # as it would arrive from a blank .env line
    )

    token = pyjwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "tenant_id": str(uuid.uuid4()),
            "iss": "auth.service.local",
            "exp": datetime.datetime.now(datetime.UTC) + datetime.timedelta(minutes=15),
        },
        "test-secret",
        algorithm="HS256",
    )

    claims = decode_token(token, settings)
    assert claims["tenant_id"]
