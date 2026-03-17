"""Pydantic schemas for Template API."""
from pydantic import BaseModel, ConfigDict


class TemplateSchema(BaseModel):
    """Response schema for template endpoints (id, path, type)."""

    id: int
    template_path: str
    picture_path: str | None

    model_config = ConfigDict(from_attributes=True)

class CvPreviewResponse(BaseModel):
    html: str
    filename: str