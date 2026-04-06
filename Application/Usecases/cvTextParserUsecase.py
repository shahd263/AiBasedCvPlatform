from typing import Any
from Application.Services.AiService import AiService
from Application.Services.FileParserService import FileParserService, CVTextExtractionError
from Application.Services.ResumeService import ResumeService


class CvTextParserUsecase:
    def __init__(self, aiService: AiService , resumeService: ResumeService ,fileParserService: FileParserService):
        self._aiService = aiService
        self._resumeService = resumeService
        self._fileParserService = fileParserService
    
    async def parse_imported_cv(self, fileContent: bytes, filename: str) -> dict[str, Any]:
        try:
            cv_text = await self._fileParserService.extract_text(fileContent, filename)
        except CVTextExtractionError as e:
            raise e
        parsed_cv = await self._aiService.parse_cv(cv_text)
        return parsed_cv

    async def parse_existing_cv(self, cvId: int) -> dict[str, Any]:
        cv = await self._resumeService.get_resume_by_id(cvId)
        if not cv:
            raise ValueError("CV not found")
        parsed_cv = await self._aiService.parse_cv(cv.extracted_text)
        return parsed_cv