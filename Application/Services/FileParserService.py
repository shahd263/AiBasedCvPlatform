import asyncio
from pathlib import Path
from docx import Document
import pdfplumber


class CVTextExtractionError(Exception):
    """Raised when text extraction from the CV file fails."""

    def __init__(self, message: str ) -> None:
        self.message = message
        super().__init__(message)
        
class FileParserService:
    def _extract_text_pdf(self, file_path: Path) -> str:
        try:
            text_parts = []
            with pdfplumber.open(file_path) as pdf:
                for page in pdf.pages:
                    t = page.extract_text()
                    if t:
                        text_parts.append(t)
            return "\n".join(text_parts).strip() if text_parts else ""
        except Exception as e:
            raise CVTextExtractionError(f"PDF text extraction failed: {e!s}") from e

    def _extract_text_docx(self, file_path: Path) -> str:
        try:
            doc = Document(file_path)
            return  "\n".join(p.text for p in doc.paragraphs if p.text).strip()
        except Exception as e:
            raise CVTextExtractionError(f"DOCX text extraction failed: {e!s}") from e

    async def extract_text(self, file_path: Path, ext: str) -> str:
        if ext == ".pdf":
            return await asyncio.to_thread(self._extract_text_pdf, file_path)
        if ext == ".docx":
            return await asyncio.to_thread(self._extract_text_docx, file_path)
        return ""
