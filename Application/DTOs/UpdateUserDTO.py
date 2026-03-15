from dataclasses import dataclass


@dataclass
class UpdateUserDTO:
    """DTO for updating a user."""

    id: int
    full_name: str | None = None
    email: str | None = None
    password: str | None = None