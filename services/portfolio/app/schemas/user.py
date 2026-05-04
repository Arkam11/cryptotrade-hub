"""
Pydantic schemas for user-related API requests and responses.

Schemas are the contract between the API and its consumers.
They validate incoming data, coerce types, and control exactly
which fields are exposed in responses — hashed_password is
never included in any response schema.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserCreate(BaseModel):
    """
    Fields required to register a new user account.
    Email is validated for correct format by Pydantic's EmailStr.
    Password minimum length is enforced here before hashing.
    """

    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8, max_length=128)

    @field_validator("full_name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Full name must not be blank")
        return v.strip()


class UserLogin(BaseModel):
    """Credentials submitted to the login endpoint."""

    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """
    Public representation of a user returned by the API.

    model_config from_attributes=True allows Pydantic to read
    values directly from SQLAlchemy ORM instances.
    """

    id: uuid.UUID
    email: EmailStr
    full_name: str
    is_active: bool
    is_verified: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """JWT token returned after successful login or registration."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds until expiry


class TokenData(BaseModel):
    """Internal model for decoded JWT payload."""

    user_id: str
