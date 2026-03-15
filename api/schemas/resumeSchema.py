"""Pydantic schemas for CV upload and Resume API."""
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ResumeResponse(BaseModel):
    """Response schema for resume endpoints."""

    id: int
    user_id: int
    file_name: str
    file_path: str
    extracted_text: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AddCvRequest(BaseModel):
    """Request body for POST /resumes (AddCv)."""

    file_path: str
    file_name: str | None = None
    extracted_text: str | None = None


class UpdateFileNameRequest(BaseModel):
    """Request body for PATCH /resumes/{resume_id}/file-name."""

    new_file_name: str


class DeleteResumeResponse(BaseModel):
    """Response for DELETE /resumes/{resume_id}."""

    message: str
