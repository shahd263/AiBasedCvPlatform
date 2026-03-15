"""Resume CRUD service (async): get by id, list by user, add, delete, update file name."""
import asyncio
from pathlib import Path

from Domain.repositories.resume_repository import ResumeRepositoryInterface
from Entites.Resume import Resume


class ResumeNotFoundError(Exception):
    """Raised when a resume is not found by id."""

    def __init__(self, resume_id: int) -> None:
        self.resume_id = resume_id
        super().__init__(f"Resume not found: id={resume_id}")


class ResumeService:
    """Handles resume CRUD: get by id, get user resumes, add, delete, update file name."""

    def __init__(self, resume_repository: ResumeRepositoryInterface) -> None:
        self._repo = resume_repository

    async def get_resume_by_id(self, resume_id: int) -> Resume:
        """Return resume by id. Raises ResumeNotFoundError if not found."""
        resume = await self._repo.get_by_id(resume_id)
        if not resume:
            raise ResumeNotFoundError(resume_id)
        return resume

    async def get_user_resumes(self, user_id: int) -> list[Resume]:
        """Return all resumes that belong to the user."""
        return await self._repo.get_resumes_by_user(user_id)

    async def add_cv(
        self,
        user_id: int,
        file_path: str,
        file_name: str | None = None,
        extracted_text: str | None = None,
    ) -> Resume:
        """Create a new resume and store it. file_name (no extension) defaults to stem of file_path."""
        name = file_name or Path(file_path).stem
        return await self._repo.create_resume(
            user_id=user_id,
            file_path=file_path,
            file_name=name,
            extracted_text=extracted_text,
        )

    async def delete_cv(self, resume_id: int) -> None:
        """Delete the resume and the local file. Raises ResumeNotFoundError if not found."""
        resume = await self._repo.get_by_id(resume_id)
        if not resume:
            raise ResumeNotFoundError(resume_id)
        file_path = Path(resume.file_path)
        if file_path.exists():
            try:
                await asyncio.to_thread(file_path.unlink, True)  # missing_ok=True
            except OSError:
                pass
        deleted = await self._repo.delete_resume(resume_id)
        if not deleted:
            raise ResumeNotFoundError(resume_id)

    async def update_file_name(self, resume_id: int, new_file_name: str) -> Resume:
        """Update file name (no extension). Raises ResumeNotFoundError if not found."""
        resume = await self._repo.get_by_id(resume_id)
        if not resume:
            raise ResumeNotFoundError(resume_id)
        new_file_name_stripped = Path(new_file_name).stem
        updated = await self._repo.update_file_name(resume_id, new_file_name_stripped)
        if not updated:
            raise ResumeNotFoundError(resume_id)
        return updated
