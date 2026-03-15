"""Domain entity: Resume (pure, no framework dependencies)."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Resume:
    """Domain resume entity."""

    id: int
    user_id: int
    file_name: str
    file_path: str
    extracted_text: str | None
    created_at: datetime
    updated_at: datetime
