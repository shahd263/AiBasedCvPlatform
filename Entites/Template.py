"""Domain entity: Template (pure, no framework dependencies)."""
from dataclasses import dataclass


@dataclass
class Template:
    """Domain template entity."""

    id: int
    template_path: str
    picture_path: str | None
