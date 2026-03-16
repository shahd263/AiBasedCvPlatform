from fastapi import APIRouter , Depends
from typing import Annotated, Any
from fastapi import  HTTPException
from Application.DTOs.AuthResultDTO import AuthResult
from Application.Services.GenerateCvService import GenerateCvService
from Application.Services.coverLetterUsecase import generate_cover_letter
from Core.dependencies import get_current_user, get_generate_cv_service
from api.schemas.generateCvRrequestSchema import CandidateDataSchema, CoverLetterRequest
from api.schemas.generateCvResponseSchema import ResumeSchema

router = APIRouter(prefix="/aiBased", tags=["aiBased"])

GenerateCvServiceDep = Annotated[GenerateCvService, Depends(get_generate_cv_service)]
CurrentUser = Annotated[AuthResult, Depends(get_current_user)]

@router.post("/generate-cv", response_model=dict[str, Any])
async def generate_cv(
    request: CandidateDataSchema,
    current_user: CurrentUser,
    service: GenerateCvServiceDep,
) -> dict[str, Any]:
    """Accept candidate data as JSON and return an ATS-optimized CV in JSON."""
    try:
        return await service.generate_cv(request.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    except Exception as e:
        # Return the real exception type/message to make debugging possible.
        raise HTTPException(
            status_code=502,
            detail=f"GenAI request failed ({type(e).__name__}): {e}",
        ) from e


@router.post("/generate-cover-letter")
async def generate_letter(request: CoverLetterRequest, current_user: CurrentUser):
    try:
        letter = await generate_cover_letter(
                request.cv,
                request.job_description
            )

        return { "letter": letter}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e

