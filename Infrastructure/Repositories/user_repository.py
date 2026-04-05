"""User repository implementation using SQLAlchemy (async)."""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from Application.DTOs import UpdateUserDTO
from Entites.User import User
from Infrastructure.Database.models.user_model import UserModel


class UserRepository():
    """SQLAlchemy async implementation of UserRepository."""

    def __init__(self, db: AsyncSession) -> None:
        self._db = db

    def _to_domain(self, model: UserModel) -> User:
        return User(
            id=model.id,
            full_name=model.full_name,
            email=model.email,
            phone_number=model.phone_number,
            country=model.country,
            gender=model.gender,
            password=model.password,
            created_at=model.created_at,
            role=model.role,
        )

    async def create_user(self, full_name: str, email: str, password_hash: str, phone_number: str, country: str, gender: str, role: str) -> User:
        email_normalized = email.strip().lower()
        model = UserModel(
            full_name=full_name,
            email=email_normalized,
            password=password_hash,
            phone_number=phone_number,
            country=country,
            gender=gender,
            role=role,
        )
        self._db.add(model)
        await self._db.commit()
        await self._db.refresh(model)
        return self._to_domain(model)

    async def get_by_email(self, email: str) -> User | None:
        email_normalized = email.strip().lower()
        result = await self._db.execute(
            select(UserModel).where(UserModel.email == email_normalized)
        )
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def get_by_id(self, user_id: int) -> User | None:
        result = await self._db.execute(select(UserModel).where(UserModel.id == user_id))
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update_user(self, request: UpdateUserDTO) -> User | None:
        result = await self._db.execute(select(UserModel).where(UserModel.id == request.id))
        model = result.scalar_one_or_none()
        if not model:
            return None
        model.full_name = request.full_name
        model.email = request.email.strip().lower()
        if request.password is not None:
            model.password = request.password
        await self._db.commit()
        await self._db.refresh(model)
        return self._to_domain(model)
