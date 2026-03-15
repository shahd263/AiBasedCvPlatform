"""Resume repository implementation using SQLAlchemy."""
from datetime import datetime
from pathlib import Path

from sqlalchemy.orm import Session

from Domain.repositories.resume_repository import ResumeRepositoryInterface
from Entites.Resume import Resume
from Infrastructure.Database.models.resume_model import ResumeModel


class ResumeRepository(ResumeRepositoryInterface):
    """SQLAlchemy implementation of ResumeRepository."""

    def __init__(self, db: Session) -> None:
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

    def create_resume(
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
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def get_by_id(self, resume_id: int) -> Resume | None:
        model = self._db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()
        return self._to_domain(model) if model else None

    def get_resumes_by_user(self, user_id: int) -> list[Resume]:
        models = self._db.query(ResumeModel).filter(ResumeModel.user_id == user_id).all()
        return [self._to_domain(m) for m in models]

    def delete_resume(self, resume_id: int) -> bool:
        model = self._db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()
        if not model:
            return False
        self._db.delete(model)
        self._db.commit()
        return True

    def update_file_name(
        self, resume_id: int, new_file_name: str) -> Resume | None:
        model = self._db.query(ResumeModel).filter(ResumeModel.id == resume_id).first()
        if not model:
            return None
        model.file_name = new_file_name
        model.updated_at = datetime.utcnow()
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)
