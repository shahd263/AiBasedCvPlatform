from fastapi import APIRouter , Depends , HTTPException
from typing import Annotated
from Application.Services.AiService import AiService  
from Core.dependencies import get_ai_service, get_cover_letter_usecase, get_preview_usecase
from api.schemas.generateCvRrequestSchema import CvGenerateRequest, CoverLetterRequest
from Application.Usecases.coverLetterUsecase import CoverLetterUsecase
from Application.Usecases.preview_Usecase import GeneratePreviewUsecase
from api.schemas.templateSchema import PreviewResponse

router = APIRouter(prefix="/aiBased", tags=["aiBased"])

AiServiceDep = Annotated[AiService, Depends(get_ai_service)]
CoverLetterUsecaseDep = Annotated[CoverLetterUsecase, Depends(get_cover_letter_usecase)]
PreviewUsecaseDep = Annotated[GeneratePreviewUsecase, Depends(get_preview_usecase)]


@router.post("/generate-cv", response_model=PreviewResponse)
async def generate_cv(
    request: CvGenerateRequest,
    usecase: PreviewUsecaseDep,
) -> PreviewResponse:
    """Accept candidate data as JSON and return an ATS-optimized CV in JSON."""
    try:
        cv_data = await usecase.cv_preview(request.template_id, request.candidate_data.model_dump())
        return PreviewResponse(html=cv_data["html"], filename=cv_data["filename"])
    except ValueError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(
            status_code=502,
            detail=f"GenAI request failed ({type(e).__name__}): {e}",
        ) from e


@router.post("/generate-cover-letter")
async def generate_letter(request: CoverLetterRequest , usecase: CoverLetterUsecaseDep):
    try:
        letter = await usecase.generate_cover_letter(request.cvId, request.job_description)

        return { "letter": letter}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error") from e

