"""Dependency injection for FastAPI."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from Application.DTOs.AuthResultDTO import AuthResult
from Application.Services.AuthenticationService import AuthenticationService
from Application.Services.GenerateService import GenerateService
from Application.Services.ResumeService import ResumeService
from Application.Services.TemplateService import TemplateService
from Domain.repositories.resume_repository import ResumeRepositoryInterface
from Domain.repositories.template_repository import TemplateRepositoryInterface
from Domain.repositories.user_repository import UserRepositoryInterface
from Infrastructure.Database.database import get_db
from Infrastructure.Repositories.resume_repository_impl import ResumeRepository
from Infrastructure.Repositories.template_repository_impl import TemplateRepository
from Infrastructure.Repositories.user_repository_impl import UserRepository

security_scheme = HTTPBearer(auto_error=False)


def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepositoryInterface:
    """Provide UserRepository implementation."""
    return UserRepository(db)


def get_authentication_service(
    repo: Annotated[UserRepositoryInterface, Depends(get_user_repository)],
) -> AuthenticationService:
    """Provide AuthenticationService."""
    return AuthenticationService(repo)


def get_resume_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResumeRepositoryInterface:
    """Provide ResumeRepository implementation."""
    return ResumeRepository(db)



def get_resume_service(
    repo: Annotated[ResumeRepositoryInterface, Depends(get_resume_repository)],
) -> ResumeService:
    """Provide ResumeService."""
    return ResumeService(repo)


def get_template_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TemplateRepositoryInterface:
    """Provide TemplateRepository implementation."""
    return TemplateRepository(db)


def get_template_service(
    repo: Annotated[TemplateRepositoryInterface, Depends(get_template_repository)],
) -> TemplateService:
    """Provide TemplateService."""
    return TemplateService(repo)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    auth_service: Annotated[AuthenticationService, Depends(get_authentication_service)],
) -> AuthResult:
    """Extract Bearer token and return current user or raise 401."""
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    result = await auth_service.get_current_user(token=credentials.credentials)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return result

def get_generate_service() -> GenerateService:
    return GenerateService()
