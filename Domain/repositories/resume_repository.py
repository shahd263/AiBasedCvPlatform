"""Repository interface for Resume (domain layer)."""
from abc import ABC, abstractmethod

from Entites.Resume import Resume


class ResumeRepositoryInterface(ABC):
    """Abstract resume repository."""

    @abstractmethod
    def create_resume(
        self,
        user_id: int,
        file_path: str,
        file_name: str,
        extracted_text: str | None = None,
    ) -> Resume:
        """Create and persist a resume. Returns domain Resume."""
        ...

    @abstractmethod
    def get_by_id(self, resume_id: int) -> Resume | None:
        """Get resume by id if exists."""
        ...

    @abstractmethod
    def get_resumes_by_user(self, user_id: int) -> list[Resume]:
        """Get all resumes for a user."""
        ...

    @abstractmethod
    def delete_resume(self, resume_id: int) -> bool:
        """Delete resume by id. Returns True if deleted, False if not found."""
        ...

    @abstractmethod
    def update_file_name(
        self, resume_id: int, new_file_name: str
    ) -> Resume | None:
        """Update file_name, file_path and updated_at. Returns updated Resume or None if not found."""
        ...
