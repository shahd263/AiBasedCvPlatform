from fastapi import APIRouter , Depends, File , HTTPException, UploadFile, status
from typing import Annotated
from Application.Services.AiService import AiService  
from Application.Services.FileParserService import CVTextExtractionError
from Application.Services.ResumeService import ResumeNotFoundError
from Application.Usecases.cvTextParserUsecase import CvTextParserUsecase
from Core.dependencies import get_ai_service, get_cover_letter_usecase, get_cv_text_parser_usecase, get_preview_usecase
from api.schemas.generateCvRrequestSchema import CandidateDataSchema, CvGenerateRequest, CoverLetterRequest
from Application.Usecases.coverLetterUsecase import CoverLetterUsecase
from Application.Usecases.preview_Usecase import GeneratePreviewUsecase
from api.schemas.templateSchema import PreviewResponse

router = APIRouter(prefix="/aiBased", tags=["aiBased"])

AiServiceDep = Annotated[AiService, Depends(get_ai_service)]
CoverLetterUsecaseDep = Annotated[CoverLetterUsecase, Depends(get_cover_letter_usecase)]
PreviewUsecaseDep = Annotated[GeneratePreviewUsecase, Depends(get_preview_usecase)]
CvTextParserUsecaseDep = Annotated[CvTextParserUsecase, Depends(get_cv_text_parser_usecase)]


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

@router.post("/import-parse-cv" , response_model=CandidateDataSchema)
async def import_parse_cv(usecase: CvTextParserUsecaseDep, file: UploadFile = File(..., description="CV file (PDF or DOCX, max 5MB)"))->CandidateDataSchema: 
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read file: {e!s}",
        ) from e
    try:
        parsed_cv = await usecase.parse_imported_cv(content, file.filename)
        return CandidateDataSchema(**parsed_cv)
    except CVTextExtractionError as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
    

@router.post("/parse-selected-cv/{cvId}" , response_model=CandidateDataSchema)
async def parse_selected_cv(usecase: CvTextParserUsecaseDep, cvId: int)->CandidateDataSchema:
    try:
        parsed_cv = await usecase.parse_existing_cv(cvId)
        return CandidateDataSchema(**parsed_cv)
    except ResumeNotFoundError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)) from e
