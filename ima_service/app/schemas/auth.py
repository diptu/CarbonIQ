# app/schemas/auth.py
from __future__ import annotations
from typing import Optional, Dict
from pydantic import BaseModel, EmailStr, Field
from fastapi import Body
from datetime import datetime, timezone
from app.core.context import current_trace_id, current_correlation_id


# -----------------------------
# API Response
# -----------------------------
class APIResponse(BaseModel):
    data: Optional[Dict] = None
    meta: Dict = Field(
        default_factory=lambda: {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "trace_id": current_trace_id.get(),
            "correlation_id": current_correlation_id.get(),
        }
    )

    class Config:
        orm_mode = True


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
