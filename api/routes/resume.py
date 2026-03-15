"""CV upload and Resume API routes."""
from typing import Annotated
from fastapi import APIRouter, Depends, File, HTTPException, status, UploadFile
from api.schemas.resumeSchema import (
    AddCvRequest,
    DeleteResumeResponse,
    ResumeResponse,
    UpdateFileNameRequest,
)
from Application.DTOs.AuthResultDTO import AuthResult
from Application.Services.ResumeService import ResumeNotFoundError, ResumeService
from Application.Services.UploadCVService import (
    CVTextExtractionError,
    InvalidCVFileError,
    UploadCVService,
)
from Core.dependencies import get_current_user, get_resume_service, get_upload_cv_service

router = APIRouter(tags=["resume"])

UploadCVServiceDep = Annotated[UploadCVService, Depends(get_upload_cv_service)]
ResumeServiceDep = Annotated[ResumeService, Depends(get_resume_service)]
CurrentUser = Annotated[AuthResult, Depends(get_current_user)]


def _resume_entity_to_response(resume) -> ResumeResponse:
    """Map domain Resume entity to Pydantic ResumeResponse."""
    return ResumeResponse(
        id=resume.id,
        user_id=resume.user_id,
        file_name=resume.file_name,
        file_path=resume.file_path,
        extracted_text=resume.extracted_text,
        created_at=resume.created_at,
        updated_at=resume.updated_at,
    )


@router.post("/upload-cv", response_model=ResumeResponse)
async def upload_cv(
    current_user: CurrentUser,
    upload_service: UploadCVServiceDep,
    file: UploadFile = File(..., description="CV file (PDF or DOCX, max 5MB)"),
) -> ResumeResponse:
    """
    Upload a CV file (PDF or DOCX, max 5MB). Validation and extraction are done in the service.
    Requires authentication.
    """
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {e!s}",
        ) from e

    try:
        resume = await upload_service.upload_cv(
            user_id=current_user.id,
            file_content=content,
            filename=file.filename or "document",
        )
    except InvalidCVFileError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message) from e
    except CVTextExtractionError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=e.message,
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save resume. Please try again.",
        ) from e

    return _resume_entity_to_response(resume)


# --- Resume CRUD ---


@router.get("/resumes", response_model=list[ResumeResponse])
async def get_user_resumes(
    current_user: CurrentUser,
    resume_service: ResumeServiceDep,
) -> list[ResumeResponse]:
    """Return all resumes that belong to the current user."""
    resumes = await resume_service.get_user_resumes(current_user.id)
    return [_resume_entity_to_response(r) for r in resumes]


@router.get("/resumes/{resume_id}", response_model=ResumeResponse)
async def get_resume_by_id(
    resume_id: int,
    current_user: CurrentUser,
    resume_service: ResumeServiceDep,
) -> ResumeResponse:
    """Return a resume by id. 404 if not found or not owned by current user."""
    try:
        resume = await resume_service.get_resume_by_id(resume_id)
    except ResumeNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    return _resume_entity_to_response(resume)


@router.post("/resumes", response_model=ResumeResponse)
async def add_cv(
    body: AddCvRequest,
    current_user: CurrentUser,
    resume_service: ResumeServiceDep,
) -> ResumeResponse:
    """Create a new resume (file_path, optional file_name and extracted_text) for the current user."""
    resume = await resume_service.add_cv(
        user_id=current_user.id,
        file_path=body.file_path,
        file_name=body.file_name,
        extracted_text=body.extracted_text,
    )
    return _resume_entity_to_response(resume)


@router.delete("/resumes/{resume_id}", response_model=DeleteResumeResponse)
async def delete_cv(
    resume_id: int,
    current_user: CurrentUser,
    resume_service: ResumeServiceDep,
) -> DeleteResumeResponse:
    """Delete a resume. 404 if not found or not owned by current user."""
    try:
        resume = await resume_service.get_resume_by_id(resume_id)
    except ResumeNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    await resume_service.delete_cv(resume_id)
    return DeleteResumeResponse(message="Resume deleted successfully")


@router.patch("/resumes/{resume_id}/file-name", response_model=ResumeResponse)
async def update_file_name(
    resume_id: int,
    body: UpdateFileNameRequest,
    current_user: CurrentUser,
    resume_service: ResumeServiceDep,
) -> ResumeResponse:
    """Update file name (and rename file on disk). 404 if not found or not owned by current user."""
    try:
        resume = await resume_service.get_resume_by_id(resume_id)
    except ResumeNotFoundError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Resume not found")
    resume = await resume_service.update_file_name(resume_id, body.new_file_name)
    return _resume_entity_to_response(resume)
