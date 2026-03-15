"""User repository implementation using SQLAlchemy."""
from sqlalchemy.orm import Session

from Application.DTOs import UpdateUserDTO
from Domain.repositories.user_repository import UserRepositoryInterface
from Entites.User import User
from Infrastructure.Database.models.user_model import UserModel


class UserRepository(UserRepositoryInterface):
    """SQLAlchemy implementation of UserRepository."""

    def __init__(self, db: Session) -> None:
        self._db = db

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            full_name=model.full_name,
            email=model.email,
            password=model.password,
            created_at=model.created_at,
        )

    def create_user(self, full_name: str, email: str, password_hash: str) -> User:
        email_normalized = email.strip().lower()
        model = UserModel(
            full_name=full_name,
            email=email_normalized,
            password=password_hash,
        )
        self._db.add(model)
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)

    def get_by_email(self, email: str) -> User | None:
        email_normalized = email.strip().lower()
        model = self._db.query(UserModel).filter(UserModel.email == email_normalized).first()
        return self._to_domain(model) if model else None

    def get_by_id(self, user_id: int) -> User | None:
        model = self._db.query(UserModel).filter(UserModel.id == user_id).first()
        return self._to_domain(model) if model else None

    def update_user(self, request: UpdateUserDTO) -> User | None:
        model = self._db.query(UserModel).filter(UserModel.id == request.id).first()
        if not model:
            return None
        model.full_name = request.full_name
        model.email = request.email.strip().lower()
        model.password = request.password
        self._db.commit()
        self._db.refresh(model)
        return self._to_domain(model)
    
