"""Service for uploading CV files: validation, text extraction, storage, and persistence."""
import re
from pathlib import Path
from Utils.file_storage import ensure_upload_dir, uuid_save_path, validate_file, InvalidCVFileError
from Domain.repositories.resume_repository import ResumeRepositoryInterface
from Entites.Resume import Resume


from Utils.text_extractor import extract_text, CVTextExtractionError


class UploadCVService:
    """Handles CV upload: validate, extract text, store file, save resume record."""

    def __init__(self, resume_repository: ResumeRepositoryInterface) -> None:
        self._resume_repository = resume_repository


    def upload_cv(
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
            save_path.write_bytes(file_content)
        except OSError as e:
            raise InvalidCVFileError(f"Failed to save file: {e!s}") from e

        try:
            extracted_text = extract_text(save_path, ext)
        except CVTextExtractionError:
            save_path.unlink(missing_ok=True)
            raise
        except Exception as e:
            save_path.unlink(missing_ok=True)
            raise CVTextExtractionError(f"Text extraction failed: {e!s}") from e

        # file_path on disk is UUID-based (e.g. uploads/5/a1b2c3d4.pdf); file_name is original name without extension
        file_path_str = str(save_path).replace("\\", "/")
        original_file_name = Path(filename).stem or "document"
        resume = self._resume_repository.create_resume(
            user_id=user_id,
            file_path=file_path_str,
            file_name=original_file_name,
            extracted_text=extracted_text or None,
        )
        return resume
