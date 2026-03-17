"""Template API routes."""
from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, status
from starlette.responses import HTMLResponse, StreamingResponse

from api.schemas.generateCvResponseSchema import CvGenerateResponse
from api.schemas.templateSchema import CvPreviewResponse, TemplateSchema
from Application.Services.TemplateService import TemplateNotFoundError, TemplateService
from Core.dependencies import get_template_service

router = APIRouter(tags=["templates"])

TemplateServiceDep = Annotated[TemplateService, Depends(get_template_service)]


def _template_entity_to_schema(template) -> TemplateSchema:
    """Map domain Template entity to Pydantic TemplateSchema."""
    return TemplateSchema(
        id=template.id,
        template_path=template.template_path,
        picture_path=template.picture_path,
    )


@router.get("/templates", response_model=list[TemplateSchema])
async def get_all_templates(
    template_service: TemplateServiceDep,
) -> list[TemplateSchema]:
    """Return all templates."""
    templates = await template_service.get_all()
    return [_template_entity_to_schema(t) for t in templates]




@router.get("/templates/{template_id}", response_model=TemplateSchema)
async def get_template_by_id(
    template_id: int,
    template_service: TemplateServiceDep,
) -> TemplateSchema:
    """Return a template by id. 404 if not found."""
    try:
        template = await template_service.get_template_by_id(template_id)
    except TemplateNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Template not found",
        )
    return _template_entity_to_schema(template)

@router.post("/cv-preview", response_model=CvPreviewResponse)
async def cv_preview(body: CvGenerateResponse, template_service: TemplateServiceDep) -> CvPreviewResponse:
    """
    Render CV as HTML for preview.
    """
    html = await template_service.render_html_template(body.template_id, body.generate_cv_response.model_dump())
    filename = body.generate_cv_response.header.fullName + " - " + body.generate_cv_response.header.jobTitle or "cv"
    return CvPreviewResponse(html=html, filename=filename)

@router.post("/save-as-pdf")
async def save_as_pdf(template_service: TemplateServiceDep,html: str = Body(..., media_type="text/html")):
    pdf_bytes = template_service.generate_pdf_from_html(html)

    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": "attachment; filename=cv.pdf"
        }
    )