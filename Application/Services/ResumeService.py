"""Resume CRUD service (async): get by id, list by user, add, delete, update file name."""
from pathlib import Path
from Entites.Resume import Resume
from Infrastructure.Repositories.resume_repository import ResumeRepository
from Application.Services.FileParserService import FileParserService, CVTextExtractionError
from Application.Services.fileStorageService import FileStorageService, InvalidCVFileError
from Utils.pdf_convertor import generate_pdf_from_html , PdfGenerationError


class ResumeNotFoundError(Exception):
    """Raised when a resume is not found by id."""

    def __init__(self, resume_id: int) -> None:
        self.resume_id = resume_id
        super().__init__(f"Resume not found: id={resume_id}")



class ResumeService:
    """Handles resume CRUD: get by id, get user resumes, add, delete, update file name."""

    def __init__(self, resume_repository: ResumeRepository, file_parser_service: FileParserService , file_storage_service: FileStorageService) -> None:
        self._repo = resume_repository
        self._file_parser_service = file_parser_service
        self._file_storage_service = file_storage_service

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
        await self._file_storage_service.delete_file(file_path)
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
            save_path = await self._file_storage_service.save_file(file_content, filename)
            try:
                extracted_text = await self._file_parser_service.extract_text(file_content, filename)
            except CVTextExtractionError:
                await self._file_storage_service.delete_file(save_path)
                raise
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
        """Generate a PDF from HTML and store it as a resume for the user"""
        file_content = generate_pdf_from_html(html)
        try:
            await self.upload_cv(user_id, file_content, filename + ".pdf")
        except (InvalidCVFileError, CVTextExtractionError):
            raise
        except Exception as e:
            raise PdfGenerationError(f"Failed to persist generated PDF: {e!s}") from e
        return file_content