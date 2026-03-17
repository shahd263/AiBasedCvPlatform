from fastapi import APIRouter , Depends , HTTPException
from typing import Annotated
from Application.Services.GenerateService import GenerateService
from Core.dependencies import get_generate_service
from api.schemas.generateCvRrequestSchema import CvGenerateRequest, CoverLetterRequest
from api.schemas.generateCvResponseSchema import CvGenerateResponse, GeneratedResumeSchema

router = APIRouter(prefix="/aiBased", tags=["aiBased"])

GenerateServiceDep = Annotated[GenerateService, Depends(get_generate_service)]


@router.post("/generate-cv", response_model=CvGenerateResponse)
async def generate_cv(
    request: CvGenerateRequest,
    service: GenerateServiceDep,
) -> CvGenerateResponse:
    """Accept candidate data as JSON and return an ATS-optimized CV in JSON."""
    try:
        cv_data = await service.generate_cv(request.candidate_data.model_dump())
        return CvGenerateResponse(template_id=request.template_id, generate_cv_response=GeneratedResumeSchema(**cv_data))
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    except Exception as e:
        # Return the real exception type/message to make debugging possible.
        raise HTTPException(
            status_code=502,
            detail=f"GenAI request failed ({type(e).__name__}): {e}",
        ) from e


@router.post("/generate-cover-letter")
async def generate_letter(request: CoverLetterRequest , service: GenerateServiceDep):
    try:
        letter = await service.generate_cover_letter(request.cv, request.job_description)

        return { "letter": letter}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e

