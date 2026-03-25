"""Dependency injection for FastAPI."""
from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from Application.DTOs.AuthResultDTO import AuthResult
from Application.Services.AuthenticationService import AuthenticationService
from Application.Services.AiService import AiService
from Application.Services.ResumeService import ResumeService
from Application.Services.TemplateService import TemplateService
from Application.Services.FileParserService import FileParserService
from Application.Services.fileStorageService import FileStorageService
from Infrastructure.Database.database import get_db
from Infrastructure.Ai.Gemini_Client import GeminiClient
from Infrastructure.Repositories.resume_repository import ResumeRepository
from Infrastructure.Repositories.template_repository import TemplateRepository
from Infrastructure.Repositories.user_repository import UserRepository
from Application.Usecases.coverLetterUsecase import CoverLetterUsecase
from Application.Usecases.preview_Usecase import GeneratePreviewUsecase


security_scheme = HTTPBearer(auto_error=False)


def get_user_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserRepository:
    """Provide UserRepository implementation."""
    return UserRepository(db)


def get_authentication_service(
    repo: Annotated[UserRepository, Depends(get_user_repository)],
) -> AuthenticationService:
    """Provide AuthenticationService."""
    return AuthenticationService(repo)


def get_resume_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> ResumeRepository:
    """Provide ResumeRepository implementation."""
    return ResumeRepository(db)


def get_file_parser_service() -> FileParserService:
    return FileParserService()

def get_file_storage_service() -> FileStorageService:
    return FileStorageService()

def get_resume_service(
    repo: Annotated[ResumeRepository, Depends(get_resume_repository)], 
    file_parser_service: Annotated[FileParserService, Depends(get_file_parser_service)],
    file_storage_service: Annotated[FileStorageService, Depends(get_file_storage_service)],
) -> ResumeService:
    """Provide ResumeService."""
    return ResumeService(repo, file_parser_service, file_storage_service)


def get_template_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TemplateRepository:
    """Provide TemplateRepository implementation."""
    return TemplateRepository(db)


def get_template_service(
    repo: Annotated[TemplateRepository, Depends(get_template_repository)],
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



def get_ai_service() -> AiService:
    return AiService(GeminiClient())

def get_cover_letter_usecase(
    ai_service: Annotated[AiService, Depends(get_ai_service)],
    resume_service: Annotated[ResumeService, Depends(get_resume_service)],
) -> CoverLetterUsecase:
    return CoverLetterUsecase(ai_service, resume_service)

def get_preview_usecase(
    ai_service: Annotated[AiService, Depends(get_ai_service)],
    template_service: Annotated[TemplateService, Depends(get_template_service)],
    resume_service: Annotated[ResumeService, Depends(get_resume_service)],
) -> GeneratePreviewUsecase:
    return GeneratePreviewUsecase(ai_service, template_service, resume_service)