"""
Data access layer for the users table.

All database queries for user records are centralised here.
Upper layers (services, API) call these methods and remain
unaware of SQL or SQLAlchemy internals.
"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UserRepository:
    """
    Encapsulates all CRUD operations for User records.

    Receives a database session via constructor injection,
    making it straightforward to inject a test session in unit tests.
    """

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        """Returns the user with the given UUID, or None if not found."""
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        """
        Returns the user with the given email address, or None.
        Used during login to retrieve credentials for verification.
        """
        result = await self.db.execute(
            select(User).where(User.email == email.lower())
        )
        return result.scalar_one_or_none()

    async def create(
        self,
        email: str,
        full_name: str,
        hashed_password: str,
    ) -> User:
        """
        Inserts a new user record and returns the persisted instance.

        The session is flushed to populate database-generated fields
        (id, created_at) without committing the transaction.
        The caller's session commit finalises the write.
        """
        user = User(
            email=email.lower(),
            full_name=full_name,
            hashed_password=hashed_password,
        )
        self.db.add(user)
        await self.db.flush()   # populate id without committing
        await self.db.refresh(user)
        return user

    async def email_exists(self, email: str) -> bool:
        """Returns True if an account with this email already exists."""
        result = await self.db.execute(
            select(User.id).where(User.email == email.lower())
        )
        return result.scalar_one_or_none() is not None
