"""
Application configuration loaded from environment variables.

Pydantic Settings reads values from the .env file and validates
their types at startup. If a required variable is missing the
application fails immediately with a clear error rather than
crashing later at runtime.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Central settings object for the portfolio service.

    All configuration is sourced from environment variables or
    a .env file in the project root. Default values are provided
    for local development only and must be overridden in production.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_name: str = "CryptoTrade Hub — Portfolio Service"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True

    # PostgreSQL — async connection string built from individual parts
    postgres_user: str = "cryptouser"
    postgres_password: str = "cryptopass"
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "cryptotrade"

    @property
    def database_url(self) -> str:
        """
        Async PostgreSQL connection string used by SQLAlchemy.
        asyncpg is the async driver; it requires the postgresql+asyncpg scheme.
        """
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def sync_database_url(self) -> str:
        """
        Synchronous connection string used only by Alembic migrations.
        Alembic does not support async connections so psycopg2 is used here.
        """
        return (
            f"postgresql://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    # Redis
    redis_host: str = "localhost"
    redis_port: int = 6379

    @property
    def redis_url(self) -> str:
        """Redis connection string."""
        return f"redis://{self.redis_host}:{self.redis_port}"

    # JWT Authentication
    secret_key: str = "change-this-in-production-use-a-long-random-string"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 30


# Single shared instance imported across the application.
# Instantiated once at module load time.
settings = Settings()
