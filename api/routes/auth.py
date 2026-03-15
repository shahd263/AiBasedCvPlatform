"""Auth API routes."""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from Application.DTOs.UpdateUserDTO import UpdateUserDTO
from api.schemas.authSchema import (
    LoginRequest,
    RegisterRequest,
    UpdateProfileRequest,
    UserResponse,
)
from Core.dependencies import get_authentication_service, get_current_user
from Application.Services.AuthenticationService import (
    AuthenticationService,
    EmailAlreadyRegisteredError,
)
from Application.DTOs.AuthResultDTO import AuthResult

router = APIRouter(prefix="/auth", tags=["auth"])

# --- Dependency Aliases ---
AuthServiceDep = Annotated[AuthenticationService, Depends(get_authentication_service)]
CurrentUser = Annotated[AuthResult, Depends(get_current_user)]


@router.post("/register", response_model=UserResponse)
async def register(
    body: RegisterRequest,
    auth_service: AuthServiceDep,
) -> UserResponse:
    """Register a new user. Returns user info and JWT."""
    try:
        result = await auth_service.register(
            full_name=body.full_name, email=body.email, password=body.password
        )
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    return UserResponse(full_name=result.full_name, email=result.email, token=result.token)


@router.post("/login", response_model=UserResponse)
async def login(
    body: LoginRequest,
    auth_service: AuthServiceDep,
) -> UserResponse:
    """Login with email/password. Returns user info and JWT."""
    result = await auth_service.login(email=body.email, password=body.password)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    return UserResponse(full_name=result.full_name, email=result.email, token=result.token)


@router.get("/me", response_model=UserResponse)
async def me(
    current_user: CurrentUser,
) -> UserResponse:
    """Return current authenticated user (from JWT)."""
    return UserResponse(
        full_name=current_user.full_name,
        email=current_user.email,
        token=current_user.token,
    )


@router.patch("/me", response_model=UserResponse)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
) -> UserResponse:
    """Update current user profile (full_name, email, and/or password). Returns updated user and new token."""
    try:
        request = UpdateUserDTO(
            id=current_user.id,
            full_name=body.full_name,
            email=body.email,
            password=body.password,
        )
        result = await auth_service.update_profile(request)
    except EmailAlreadyRegisteredError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return UserResponse(full_name=result.full_name, email=result.email, token=result.token)