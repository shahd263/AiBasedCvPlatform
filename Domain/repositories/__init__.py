"""Repository interfaces."""
from Domain.repositories.user_repository import UserRepositoryInterface
from Domain.repositories.resume_repository import ResumeRepositoryInterface

__all__ = ["UserRepositoryInterface", "ResumeRepositoryInterface"]
