from dataclasses import dataclass


@dataclass
class ProfileDTO:
    """Result of register/login/get_current_user (maps to UserResponse)."""
    full_name: str
    email: str
    phone_number: str
    country: str
    gender: str
