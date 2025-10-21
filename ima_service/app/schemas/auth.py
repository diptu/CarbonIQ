# app/schemas/auth.py
from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field


# -----------------------------
# Login Request
# -----------------------------
class LoginRequest(BaseModel):
    email: EmailStr = Field(..., example="user@example.com")
    password: str = Field(..., min_length=8, example="strongpassword")
