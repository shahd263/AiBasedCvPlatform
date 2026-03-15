from dataclasses import dataclass


@dataclass
class AuthResult:
    """Result of register/login/get_current_user (maps to UserResponse)."""
    id: int
    full_name: str
    email: str
    token: str