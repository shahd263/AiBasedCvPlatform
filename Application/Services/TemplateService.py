"""Template service: get CV/CL templates and by id."""
from typing import Any
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from Infrastructure.Repositories.template_repository import TemplateRepository
from Entites.Template import Template

TEMPLATES_DIR = Path(__file__).parent.parent.parent / "Templates" / "Cvs"


class TemplateNotFoundError(Exception):
    """Raised when a template is not found by id."""

    def __init__(self, template_id: int) -> None:
        self.template_id = template_id
        super().__init__(f"Template not found: id={template_id}")



class TemplateService:
    """Handles template queries: get all templates, get by id."""

    def __init__(self, template_repository: TemplateRepository) -> None:
        self._repo = template_repository

    async def get_all(self) -> list[Template]:
        """Return all templates."""
        return await self._repo.get_all()

    async def get_template_by_id(self, template_id: int) -> Template:
        """Return template by id. Raises TemplateNotFoundError if not found."""
        template = await self._repo.get_by_id(template_id)
        if not template:
            raise TemplateNotFoundError(template_id)
        return template
    

    async def render_html_template(self, template_id: int, response: dict[str, Any]) -> str:
        template = await self.get_template_by_id(template_id)
        if not template:
            raise TemplateNotFoundError(template_id)
        env = Environment(loader=FileSystemLoader(TEMPLATES_DIR))
        filename = template.template_path.split("/")[-1]
        template = env.get_template(filename)
        html = template.render(response=response)
        return html
    

               


    # def generate_pdf(self, resume: GeneratedResumeSchema) -> bytes:
    #     html = self.render_cv_html(resume)
    #     pdf = HTML(string=html).write_pdf()
    #     return pdf

