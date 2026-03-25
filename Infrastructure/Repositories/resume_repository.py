"""Resume repository implementation using SQLAlchemy (async)."""
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Entites.Resume import Resume
from Infrastructure.Database.models.resume_model import ResumeModel


class ResumeRepository():
    """SQLAlchemy async implementation of ResumeRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    def _to_domain(self, model: ResumeModel) -> Resume:
        file_name = model.file_name if model.file_name is not None else Path(model.file_path).stem
        return Resume(
            id=model.id,
            user_id=model.user_id,
            file_name=file_name,
            file_path=model.file_path,
            extracted_text=model.extracted_text,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create_resume(
        self,
        user_id: int,
        file_path: str,
        file_name: str,
        extracted_text: str | None = None,
    ) -> Resume:
        model = ResumeModel(
            user_id=user_id,
            file_path=file_path,
            file_name=file_name,
            extracted_text=extracted_text,
        )
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return self._to_domain(model)

    async def get_by_id(self, resume_id: int) -> Resume | None:
        result = await self._db.execute(select(ResumeModel).where(ResumeModel.id == resume_id))
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_resumes_by_user(self, user_id: int) -> list[Resume]:
        result = await self._db.execute(
            select(ResumeModel).where(ResumeModel.user_id == user_id)
        )
        models = result.scalars().all()
        return [self._to_domain(m) for m in models]

    async def delete_resume(self, resume_id: int) -> bool:
        result = await self._db.execute(select(ResumeModel).where(ResumeModel.id == resume_id))
        model = result.scalar_one_or_none()
        if not model:
            return False
        await self._db.delete(model)
        await self._db.commit()
        return True

    async def update_file_name(
        self, resume_id: int, new_file_name: str
    ) -> Resume | None:
        result = await self._db.execute(select(ResumeModel).where(ResumeModel.id == resume_id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        model.file_name = new_file_name
        model.updated_at = datetime.utcnow()
        await self._db.commit()
        await self._db.refresh(model)
        return self._to_domain(model)
