"""Auth API routes."""
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from Application.DTOs.UpdateUserDTO import UpdateUserDTO
from api.schemas.authSchema import (
    LoginRequest,
    ProfileResponse,
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
            full_name=body.full_name, email=body.email, 
            password=body.password, phone_number=body.phone_number, 
            country=body.country, gender=body.gender,
            role=body.role,
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


@router.get("/me", response_model=ProfileResponse)
async def me(
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
) -> ProfileResponse:
    """Return current authenticated user (from JWT)."""
    user = await auth_service.get_user_by_id(current_user.id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return ProfileResponse(
        full_name=user.full_name,
        email=user.email,
        phone_number=user.phone_number,
        country=user.country,
        gender=user.gender,
        role=user.role,
        status=user.status,
    )
    


@router.patch("/me", response_model=ProfileResponse)
async def update_profile(
    body: UpdateProfileRequest,
    current_user: CurrentUser,
    auth_service: AuthServiceDep,
) -> ProfileResponse:
    """Update current user profile (full_name, email, and/or password). Returns updated user and new token."""
    try:
        request = UpdateUserDTO(
            id=current_user.id,
            full_name=body.full_name,
            email=body.email,
            password=body.password,
            phone_number=body.phone_number,
            country=body.country,
            gender=body.gender,
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
    return ProfileResponse(
        full_name=result.full_name,
        email=result.email,
        phone_number=result.phone_number,
        country=result.country,
        gender=result.gender,
        role=result.role,
        status=result.status,
    )