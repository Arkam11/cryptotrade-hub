"""
Alembic migration environment.

Connects Alembic to the application's SQLAlchemy metadata and
database URL from the settings object. Supports both online
(direct DB connection) and offline (SQL script generation) modes.
"""

from logging.config import fileConfig

import app.models  # noqa: F401 — registers all models with Base.metadata
from alembic import context
from app.core.config import settings
from app.core.database import Base
from sqlalchemy import engine_from_config, pool

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Alembic compares Base.metadata against the live database schema
# to determine what migrations are needed.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """
    Generates migration SQL scripts without a live database connection.
    Useful for reviewing changes before applying them.
    """
    context.configure(
        url=settings.sync_database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Applies migrations directly against a live database connection.
    Used during local development and in CI/CD pipelines.
    """
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = settings.sync_database_url

    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
