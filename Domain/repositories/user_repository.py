"""Repository interface for User (domain layer)."""
from abc import ABC, abstractmethod

from Application.DTOs.UpdateUserDTO import UpdateUserDTO
from Entites.User import User


class UserRepositoryInterface(ABC):
    """Abstract user repository."""

    @abstractmethod
    def create_user(self, full_name: str, email: str, password_hash: str) -> User:
        """Create and persist a user. Returns domain User."""
        ...

    @abstractmethod
    def get_by_email(self, email: str) -> User | None:
        """Get user by email if exists."""
        ...

    @abstractmethod
    def get_by_id(self, user_id: int) -> User | None:
        """Get user by id if exists."""
        ...

    @abstractmethod
    def update_user(self, request: UpdateUserDTO) -> User | None:
        """Update user by id. Only provided fields are updated. Returns updated User or None."""
        ...
