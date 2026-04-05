"""Domain entity: User (pure, no framework dependencies)."""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class User:
    """Domain user entity."""

    id: int
    full_name: str
    email: str
    phone_number: str
    country: str
    gender: str
    password: str
    created_at: datetime
