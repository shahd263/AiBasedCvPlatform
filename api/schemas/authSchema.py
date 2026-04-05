"""Pydantic schemas for auth API."""
from pydantic import BaseModel, EmailStr


class UserResponse(BaseModel):
    """Response schema for auth endpoints: full_name, email, token."""

    full_name: str
    email: EmailStr
    token: str



class RegisterRequest(BaseModel):
    """Request body for POST /auth/register."""

    full_name: str
    email: EmailStr
    password: str
    phone_number: str
    country: str
    gender: str


class LoginRequest(BaseModel):
    """Request body for POST /auth/login."""

    email: EmailStr
    password: str



class UpdateProfileRequest(BaseModel):
    """Request body for PATCH /api/auth/me (all fields optional)."""

    full_name: str | None = None
    email: EmailStr | None = None
    phone_number: str | None = None
    country: str | None = None
    gender: str | None = None
    password: str | None = None


class ProfileResponse(BaseModel):
    """Response schema for auth endpoints: full_name, email, phone_number, country, gender."""
    full_name: str
    email: EmailStr
    phone_number: str
    country: str | None = None
    gender: str | None = None
