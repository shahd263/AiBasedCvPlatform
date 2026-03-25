"""Authentication service: register, login, get current user (async)."""
from Application.DTOs.AuthResultDTO import AuthResult
from Application.DTOs.UpdateUserDTO import UpdateUserDTO
from Core.security import create_access_token, decode_token, hash_password, verify_password
from Infrastructure.Repositories.user_repository import UserRepository


class EmailAlreadyRegisteredError(Exception):
    """Raised when registering with an email that already exists."""

    pass


class AuthenticationService:
    """Handles user registration, login, current user, and logout."""

    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repository = user_repository

    async def register(self, full_name: str, email: str, password: str) -> AuthResult:
        """Register a new user: hash password, save, return JWT."""
        if await self._email_exists(email):
            raise EmailAlreadyRegisteredError(f"Email already registered: {email}")
        user = await self._user_repository.create_user(
            full_name=full_name,
            email=email,
            password_hash=hash_password(password),
        )
        token = create_access_token(user_id=user.id, email=user.email)
        return AuthResult(id=user.id, full_name=user.full_name, email=user.email, token=token)

    async def login(self, email: str, password: str) -> AuthResult | None:
        """Validate email/password and return JWT or None."""
        user = await self._user_repository.get_by_email(email)
        if not user or not verify_password(password, user.password):
            return None
        token = create_access_token(user_id=user.id, email=user.email)
        return AuthResult(id=user.id, full_name=user.full_name, email=user.email, token=token)

    async def get_current_user(self, token: str) -> AuthResult | None:
        """Decode JWT and return user info or None."""
        payload = decode_token(token)
        if not payload:
            return None
        user_id_str = payload.get("sub")
        email = payload.get("email")
        if not user_id_str or not email:
            return None
        try:
            user_id = int(user_id_str)
        except ValueError:
            return None
        user = await self._user_repository.get_by_id(user_id)
        if not user:
            return None
        return AuthResult(id=user.id, full_name=user.full_name, email=user.email, token=token)

    async def update_profile(self, request: UpdateUserDTO) -> AuthResult | None:
        """Update current user profile. Returns new AuthResult or None."""
        email_normalized = request.email.strip().lower()
        existing = await self._user_repository.get_by_email(email_normalized)
        if existing and existing.id != request.id:
            raise EmailAlreadyRegisteredError(f"Email already registered: {request.email}")
        if request.password is not None and request.password.strip():
            request.password = hash_password(request.password)
        else:
            request.password = None
        user = await self._user_repository.update_user(request)
        if not user:
            return None
        token = create_access_token(user_id=user.id, email=user.email)
        return AuthResult(id=user.id, full_name=user.full_name, email=user.email, token=token)

    async def _email_exists(self, email: str) -> bool:
        email_normalized = email.strip().lower()
        existing = await self._user_repository.get_by_email(email_normalized)
        return existing is not None
