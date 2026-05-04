"""
ORM model registry.

Importing all models here ensures SQLAlchemy's metadata object
is aware of every table when Alembic generates migrations.
"""

from app.models.user import User

__all__ = ["User"]
