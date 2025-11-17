"""API routes for authentication."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db
from src.services.auth_service import AuthService
from src.api.schemas.auth_schemas import (
    UserRegister,
    UserLogin,
    TokenResponse,
    UserResponse,
)
from src.api.middleware.auth import get_current_user


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    db: AsyncSession = Depends(get_db),
):
    """Register a new user.

    Args:
        user_data: User registration data
        db: Database session

    Returns:
        Created user information
    """
    service = AuthService(db)
    user = await service.register_user(user_data)

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at.isoformat(),
    )


@router.post("/login", response_model=TokenResponse)
async def login(
    login_data: UserLogin,
    db: AsyncSession = Depends(get_db),
):
    """Authenticate user and get access token.

    Args:
        login_data: User login credentials
        db: Database session

    Returns:
        Access token and token information
    """
    service = AuthService(db)
    auth_result = await service.authenticate_user(login_data)

    return TokenResponse(
        access_token=auth_result["access_token"],
        token_type=auth_result["token_type"],
        expires_in=auth_result["expires_in"],
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get current authenticated user information.

    Args:
        current_user: Current authenticated user from JWT token
        db: Database session

    Returns:
        Current user information
    """
    from uuid import UUID

    service = AuthService(db)
    user = await service.get_user_by_id(UUID(current_user["user_id"]))

    return UserResponse(
        id=str(user.id),
        email=user.email,
        full_name=user.full_name,
        created_at=user.created_at.isoformat(),
    )
