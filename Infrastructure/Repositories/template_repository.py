"""Template repository implementation using SQLAlchemy (async)."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Entites.Template import Template
from Infrastructure.Database.models.template_model import TemplateModel


class TemplateRepository():
    """SQLAlchemy async implementation of TemplateRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    def _to_domain(self, model: TemplateModel) -> Template:
        return Template(
            id=model.id,
            template_path=model.template_path,
            picture_path=model.picture_path,
            description=model.description,
        )

    async def get_by_id(self, template_id: int) -> Template | None:
        result = await self._db.execute(
            select(TemplateModel).where(TemplateModel.id == template_id)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_all(self) -> list[Template]:
        result = await self._db.execute(
            select(TemplateModel)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]
