import re
import uuid
from pathlib import Path

# Allowed extensions and MIME-type hints for validation
ALLOWED_EXTENSIONS = {".pdf", ".docx"}
MAX_FILE_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
UPLOAD_DIR = Path("uploads")

class InvalidCVFileError(Exception):
    """Raised when file type or size is invalid."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)


def ensure_upload_dir() -> Path:
    """Ensure uploads/user_id/ exists and return it."""
    user_dir = UPLOAD_DIR 
    user_dir.mkdir(parents=True, exist_ok=True)
    return user_dir



def uuid_save_path(base_dir: Path, ext: str) -> Path:
    """Return a unique path using UUID for the file on disk: base_dir/{uuid}{ext}."""
    return base_dir / f"{uuid.uuid4().hex}{ext}"

def validate_file(filename: str, file_size: int) -> str:
    """Validate filename and size. Returns normalized extension."""
    ext = Path(filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidCVFileError(
            f"Invalid file type. Allowed: PDF, DOCX. Got: {ext or 'unknown'}"
        )
    if file_size > MAX_FILE_SIZE_BYTES:
        raise InvalidCVFileError(
            f"File too large. Maximum size is {MAX_FILE_SIZE_BYTES // (1024*1024)}MB."
        )
    if file_size <= 0:
        raise InvalidCVFileError("File is empty.")
    return ext

