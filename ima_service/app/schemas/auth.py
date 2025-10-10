# app/schemas/auth.py
from pydantic import BaseModel, constr, EmailStr


class LoginSchema(BaseModel):
    email: EmailStr
    password: constr(min_length=8, max_length=128)


class TokenSchema(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # in seconds
    tenant_id: str
