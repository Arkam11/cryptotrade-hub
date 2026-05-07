"""
Pytest configuration and shared fixtures.

Uses an in-memory SQLite database for fast, isolated tests.
Each test gets a clean session with no leftover data.
The real database dependency is overridden so tests never
touch the PostgreSQL instance running in Docker.
"""

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.main import app

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture(scope="session")
async def test_engine():
    """
    Creates the SQLite engine and all tables once per test session.
    Tables are dropped after the session completes.
    """
    engine = create_async_engine(
        TEST_DATABASE_URL,
        echo=False,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine.sync_engine, "connect")
    def set_sqlite_pragma(dbapi_conn, connection_record):
        cursor = dbapi_conn.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_engine):
    """
    Provides an isolated database session per test.
    All writes are rolled back after each test completes.
    """
    session_factory = async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
    async with session_factory() as session:
        yield session
        await session.rollback()


@pytest_asyncio.fixture
async def client(db_session):
    """
    Async HTTP test client with database dependency overridden.
    Requests go through the real FastAPI app but write to the
    isolated test session instead of the production database.
    """
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac

    app.dependency_overrides.clear()
