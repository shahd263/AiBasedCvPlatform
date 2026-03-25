import asyncio
import uuid
from pathlib import Path

# Allowed extensions and MIME-type hints for validation

class InvalidCVFileError(Exception):
    """Raised when file type or size is invalid."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


class FileStorageService:
    ALLOWED_EXTENSIONS = {".pdf", ".docx"}
    MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
    UPLOAD_DIR = Path("uploads")

    async def save_file(self, file_content: bytes, filename: str) -> Path:
        """Save file to uploads/ and return the path."""
        file_size = len(file_content)
        ext = self._validate_file(filename, file_size)
        save_path = self.UPLOAD_DIR / f"{uuid.uuid4().hex}{ext}"
        try:
            await asyncio.to_thread(save_path.write_bytes, file_content)
        except OSError as e:
            raise InvalidCVFileError(f"Failed to save file: {e!s}") from e
        return save_path

    async def delete_file(self, file_path: Path) -> None:
        """Delete file from disk."""
        if file_path.exists():
            try:
                await asyncio.to_thread(file_path.unlink, True)
            except OSError as e:
                raise InvalidCVFileError(f"Failed to delete file: {file_path!s}") from e

    def _validate_file(self, filename: str, file_size: int) -> str:
        """Validate filename and size. Returns normalized extension."""
        ext = Path(filename).suffix.lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise InvalidCVFileError(
                f"Invalid file type. Allowed: PDF, DOCX. Got: {ext or 'unknown'}"
            )
        if file_size > self.MAX_FILE_SIZE_BYTES:
            raise InvalidCVFileError(
                f"File too large. Maximum size is {self.MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
            )
        if file_size <= 0:
            raise InvalidCVFileError("File is empty.")
        return ext
