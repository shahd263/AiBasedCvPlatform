class PdfGenerationError(Exception):
    """Raised when generating or storing a PDF representation of a resume fails."""

from weasyprint import HTML

def generate_pdf_from_html(html: str) -> bytes:
    try:
        return HTML(string=html).write_pdf()
    except Exception as e:
        raise PdfGenerationError(f"Failed to generate PDF from HTML: {e!s}") from e

