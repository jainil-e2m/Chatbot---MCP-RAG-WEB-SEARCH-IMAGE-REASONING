"""
Authentication schemas for request/response validation.
"""
from pydantic import BaseModel, EmailStr, field_validator


class SignupRequest(BaseModel):
    """Signup request schema."""
    name: str
    email: EmailStr
    password: str
    confirm_password: str

    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    @field_validator('password')
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError('Password must be at least 6 characters long')
        return v


class LoginRequest(BaseModel):
    """Login request schema."""
    email: EmailStr
    password: str


class SignupResponse(BaseModel):
    """Signup response schema."""
    user_id: str
    name: str
    email: str
    token: str


class LoginResponse(BaseModel):
    """Login response schema."""
    user_id: str
    name: str
    email: str
    token: str
