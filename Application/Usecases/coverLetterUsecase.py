from Application.Services.AiService import AiService
from Application.Services.ResumeService import ResumeService


class CoverLetterUsecase:
    def __init__(self, aiService: AiService, resumeService: ResumeService):
        self._aiService = aiService
        self._resumeService = resumeService


    async def generate_cover_letter(self, cvId: int, jobDescription: str):
        cv = await self._resumeService.get_resume_by_id(cvId)
        if not cv:
            raise ValueError("CV not found")
        letter = await self._aiService.generate_cover_letter(cv.extracted_text, jobDescription)
        return letter
