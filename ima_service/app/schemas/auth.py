# app/schemas/auth.py
from __future__ import annotations
from typing import Optional, Dict, Any
from pydantic import BaseModel, EmailStr, Field
from fastapi import Body
from datetime import datetime, timezone
from app.core.context import current_trace_id, current_correlation_id


# -----------------------------
# API Response
# -----------------------------
class APIResponse(BaseModel):
    status_code: int = 200
    message: str = "Success"
    data: Optional[Dict[str, Any]] = None
    meta: Dict[str, Any] = Field(
        default_factory=lambda: {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": current_trace_id.get(),
            "correlation_id": current_correlation_id.get(),
        }
    )

    class Config:
        orm_mode = True

    @classmethod
    def success(
        cls, data: Optional[Dict[str, Any]] = None, message: str = "Success", status_code: int = 200
    ):
        return cls(status_code=status_code, message=message, data=data)

    @classmethod
    def error(cls, message: str, status_code: int = 400, data: Optional[Dict[str, Any]] = None):
        return cls(status_code=status_code, message=message, data=data)


# -----------------------------
# Login Request
# -----------------------------
class LoginRequest(BaseModel):
    email: EmailStr = Body(..., example="user@example.com")
    password: str = Body(..., example="secure_password")


# -----------------------------
# Refresh Request
# -----------------------------
class RefreshRequest(BaseModel):
    refresh_token: str = Body(..., example="refresh_token_string")
