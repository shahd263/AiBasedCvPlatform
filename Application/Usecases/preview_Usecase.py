from typing import Any
from Application.Services.AiService import AiService
from Application.Services.ResumeService import ResumeService
from Application.Services.TemplateService import TemplateService
from api.schemas.generateCvResponseSchema import GeneratedResumeSchema


class GeneratePreviewUsecase:
    def __init__(self, aiService: AiService, templateService: TemplateService , resumeService: ResumeService):
        self._aiService = aiService
        self._templateService = templateService
        self._resumeService = resumeService


    async def cv_preview(self,template_id : int , candidate_data: dict[str, Any]) -> dict[str,Any]:

        cv_data = GeneratedResumeSchema(**await self._aiService.generate_cv(candidate_data))
        print(cv_data)
        html = await self._templateService.render_html_template(template_id, response=cv_data.model_dump())
        filename = cv_data.header.fullName + " - " + cv_data.header.jobTitle or "document"
        return {
            "html" : html,
            "filename":filename,
        }



    async def cover_letter_preview(self,template_id : int ,cvId: int, job_description: str) -> dict[str,Any]:
        cv = await self._resumeService.get_resume_by_id(cvId)
        if not cv:
            raise ValueError("CV not found")
        cover_letter = await self._aiService.generate_cover_letter(cv.extracted_text, job_description)
        html = await self._templateService.render_html_template(template_id, cover_letter)
        
        return {
            "html": html
        }