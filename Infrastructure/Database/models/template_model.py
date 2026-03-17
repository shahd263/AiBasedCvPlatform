"""SQLAlchemy ORM model for Template."""
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from Infrastructure.Database.base import Base


class TemplateModel(Base):
    """SQLAlchemy model for templates table."""

    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    template_path: Mapped[str] = mapped_column(String(500), nullable=False)
    picture_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
