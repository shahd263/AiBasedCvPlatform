"""Pydantic schemas for auth API."""
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """Response schema for auth endpoints: full_name, email, token."""

    full_name: str
    email: EmailStr
    token: str

    class Config:
        from_attributes = True


class RegisterRequest(BaseModel):
    """Request body for POST /auth/register."""

    full_name: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    """Request body for POST /auth/login."""

    email: EmailStr
    password: str


class LogoutResponse(BaseModel):
    """Response for POST /auth/logout."""

    success: bool
    message: str


class UpdateProfileRequest(BaseModel):
    """Request body for PATCH /api/auth/me (all fields optional)."""

    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None
