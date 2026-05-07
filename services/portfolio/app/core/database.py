"""
Async database engine and session management.

SQLAlchemy 2.0 with asyncpg provides non-blocking database access.
Each request receives an isolated session via the get_db dependency,
ensuring transactions do not leak between requests.
"""

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

# The async engine manages the connection pool.
# pool_pre_ping=True tests connections before use, recovering from
# dropped connections without raising errors to the caller.
engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,       # logs all SQL statements in development
    pool_pre_ping=True,
    pool_size=10,              # maximum persistent connections
    max_overflow=20,           # extra connections allowed under load
)

# Session factory — creates new AsyncSession instances on demand.
# expire_on_commit=False keeps ORM objects usable after a commit
# without requiring an extra database round-trip.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy ORM models.

    Every model in the application inherits from this class.
    SQLAlchemy uses it to track all table definitions and generate
    migration targets for Alembic.
    """
    pass


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI dependency that provides a database session per request.

    Usage in an endpoint:
        async def my_endpoint(db: AsyncSession = Depends(get_db)):

    The session is automatically committed on success and rolled
    back on any exception, then closed regardless of outcome.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
