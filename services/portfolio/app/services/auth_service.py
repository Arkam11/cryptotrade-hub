"""
Authentication business logic — registration and login.

The service layer sits between the API (HTTP concerns) and the
repository (database concerns). It enforces business rules:
duplicate email prevention, password verification, and token
generation. It has no knowledge of HTTP request/response objects.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.user_repository import UserRepository
from app.schemas.user import TokenResponse, UserCreate, UserResponse


class AuthenticationError(Exception):
    """Raised when login credentials are invalid."""
    pass


class DuplicateEmailError(Exception):
    """Raised when a registration email is already in use."""
    pass


class AuthService:
    """
    Handles user registration and authentication.

    Depends on UserRepository for persistence and security
    utilities for hashing and token generation.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.repo = UserRepository(db)

    async def register(self, data: UserCreate) -> tuple[UserResponse, TokenResponse]:
        """
        Creates a new user account.

        Steps:
          1. Verify the email is not already registered.
          2. Hash the plain-text password.
          3. Persist the new user record.
          4. Issue a JWT access token immediately so the client
             is authenticated without a separate login step.

        Raises DuplicateEmailError if the email is already taken.
        """
        if await self.repo.email_exists(data.email):
            raise DuplicateEmailError(f"Email already registered: {data.email}")

        hashed = hash_password(data.password)

        user = await self.repo.create(
            email=data.email,
            full_name=data.full_name,
            hashed_password=hashed,
        )

        token = create_access_token(subject=str(user.id))

        return (
            UserResponse.model_validate(user),
            TokenResponse(
                access_token=token,
                expires_in=settings.jwt_expire_minutes * 60,
            ),
        )

    async def login(self, email: str, password: str) -> tuple[UserResponse, TokenResponse]:
        """
        Authenticates a user with email and password.

        Steps:
          1. Look up the user by email.
          2. Verify the submitted password against the stored hash.
          3. Confirm the account is active.
          4. Issue a new JWT access token.

        Raises AuthenticationError for any failure — the same error
        is used whether the email is unknown or the password is wrong,
        preventing user enumeration attacks.
        """
        user = await self.repo.get_by_email(email)

        if not user or not verify_password(password, user.hashed_password):
            raise AuthenticationError("Invalid email or password")

        if not user.is_active:
            raise AuthenticationError("Account is deactivated")

        token = create_access_token(subject=str(user.id))

        return (
            UserResponse.model_validate(user),
            TokenResponse(
                access_token=token,
                expires_in=settings.jwt_expire_minutes * 60,
            ),
        )
