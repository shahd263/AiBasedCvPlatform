"""Resume CRUD service (async): get by id, list by user, add, delete, update file name."""
import asyncio
from pathlib import Path
from Domain.repositories.resume_repository import ResumeRepositoryInterface
from Entites.Resume import Resume
from weasyprint import HTML

from Utils.file_storage import (
    InvalidCVFileError,
    ensure_upload_dir,
    uuid_save_path,
    validate_file,
)
from Utils.text_extractor import CVTextExtractionError, extract_text


class ResumeNotFoundError(Exception):
    """Raised when a resume is not found by id."""

    def __init__(self, resume_id: int) -> None:
        self.resume_id = resume_id
        super().__init__(f"Resume not found: id={resume_id}")


class PdfGenerationError(Exception):
    """Raised when generating or storing a PDF representation of a resume fails."""


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
        resume = await self.get_resume_by_id(resume_id)
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

    async def upload_cv(
            self,
            user_id: int,
            file_content: bytes,
            filename: str,
        ) -> Resume:
            """
            Validate file, save to uploads/, extract text, persist Resume.
            Returns domain Resume entity.
            """
            file_size = len(file_content)
            ext = validate_file(filename, file_size)

            upload_dir = ensure_upload_dir()
            save_path = uuid_save_path(upload_dir, ext)
            try:
                await asyncio.to_thread(save_path.write_bytes, file_content)
            except OSError as e:
                raise InvalidCVFileError(f"Failed to save file: {e!s}") from e

            try:
                extracted_text = await asyncio.to_thread(extract_text, save_path, ext)
            except CVTextExtractionError:
                await asyncio.to_thread(save_path.unlink, True)
                raise
            except Exception as e:
                await asyncio.to_thread(save_path.unlink, True)
                raise CVTextExtractionError(f"Text extraction failed: {e!s}") from e

            file_path_str = str(save_path).replace("\\", "/")
            original_file_name = Path(filename).stem or "document"
            resume = await self.add_cv(
                user_id=user_id,
                file_path=file_path_str,
                file_name=original_file_name,
                extracted_text=extracted_text or None,
            )
            return resume

    async def generate_pdf_from_html(self, html: str ,filename: str, user_id: int) -> bytes:
        """Generate a PDF from HTML and store it as a resume for the user.

        Raises:
            InvalidCVFileError: if the generated file doesn't pass validation.
            CVTextExtractionError: if text extraction from the generated PDF fails.
            PdfGenerationError: for low‑level PDF generation or persistence failures.
        """
        try:
            file_content = HTML(string=html).write_pdf()
        except Exception as e:
            # Critical failure while rendering HTML to PDF (e.g. invalid HTML/CSS or engine error)
            raise PdfGenerationError(f"Failed to generate PDF from HTML: {e!s}") from e

        try:
            await self.upload_cv(user_id, file_content, filename + ".pdf")
        except (InvalidCVFileError, CVTextExtractionError):
            # Let validation/text‑extraction errors propagate as‑is so the API can respond appropriately
            raise
        except Exception as e:
            # Critical failure during persistence (e.g. database or filesystem issue)
            raise PdfGenerationError(f"Failed to persist generated PDF: {e!s}") from e

        return file_content