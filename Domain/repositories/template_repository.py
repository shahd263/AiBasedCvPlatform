"""Repository interface for Template (domain layer)."""
from abc import ABC, abstractmethod

from Entites.Template import Template


class TemplateRepositoryInterface(ABC):
    """Abstract template repository."""

    @abstractmethod
    async def get_by_id(self, template_id: int) -> Template | None:
        """Get template by id if exists."""
        ...

    @abstractmethod
    async def get_all(self) -> list[Template]:
        """Get all templates."""
        ...
