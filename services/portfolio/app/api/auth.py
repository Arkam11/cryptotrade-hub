"""
Authentication endpoints — registration and login.

The router handles HTTP concerns only: parsing request bodies,
mapping service exceptions to HTTP status codes, and shaping
responses. Business logic lives entirely in AuthService.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import TokenResponse, UserCreate, UserLogin, UserResponse
from app.services.auth_service import AuthService, AuthenticationError, DuplicateEmailError

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=dict,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    data: UserCreate,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Creates a new user account and returns an access token.

    The client receives a JWT immediately after registration —
    a separate login step is not required.
    """
    service = AuthService(db)
    try:
        user, token = await service.register(data)
    except DuplicateEmailError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    return {"user": user.model_dump(), "token": token.model_dump()}


@router.post(
    "/login",
    response_model=dict,
    summary="Authenticate and receive an access token",
)
async def login(
    data: UserLogin,
    db: AsyncSession = Depends(get_db),
) -> dict:
    """
    Validates credentials and returns a JWT access token.

    The token must be included in the Authorization header as
    'Bearer <token>' for all protected endpoints.
    """
    service = AuthService(db)
    try:
        user, token = await service.login(data.email, data.password)
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        )
    return {"user": user.model_dump(), "token": token.model_dump()}


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Return the currently authenticated user",
)
async def get_me(current_user: User = Depends(get_current_user)) -> User:
    """
    Returns the profile of the user who owns the submitted JWT.
    This endpoint is used to verify a token is still valid.
    """
    return current_user
