"""Service for uploading CV files (async): validation, text extraction, storage, persistence."""
import asyncio
from pathlib import Path

from Domain.repositories.resume_repository import ResumeRepositoryInterface
from Entites.Resume import Resume
from Utils.file_storage import (
    InvalidCVFileError,
    ensure_upload_dir,
    uuid_save_path,
    validate_file,
)
from Utils.text_extractor import CVTextExtractionError, extract_text


class UploadCVService:
    """Handles CV upload: validate, extract text, store file, save resume record."""

    def __init__(self, resume_repository: ResumeRepositoryInterface) -> None:
        self._resume_repository = resume_repository

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
        resume = await self._resume_repository.create_resume(
            user_id=user_id,
            file_path=file_path_str,
            file_name=original_file_name,
            extracted_text=extracted_text or None,
        )
        return resume
