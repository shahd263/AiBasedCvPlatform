from dataclasses import dataclass


@dataclass
class UpdateUserDTO:
    """DTO for updating a user."""

    id: int
    full_name: str | None = None
    email: str | None = None
    phone_number: str | None = None
    country: str | None = None
    gender: str | None = None
    password: str | None = None