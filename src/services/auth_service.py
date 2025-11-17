"""Service layer for authentication."""
from typing import Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from src.models.user import User
from src.api.schemas.auth_schemas import UserRegister, UserLogin
from src.core.security import hash_password, verify_password, create_access_token
from src.core.config import settings
from src.api.middleware.error_handler import BusinessRuleViolationException


class AuthService:
    """Service for user authentication."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_user(self, user_data: UserRegister) -> User:
        """Register a new user.

        Args:
            user_data: User registration data

        Returns:
            Created user

        Raises:
            BusinessRuleViolationException: If email already exists
        """
        # Check if email already exists
        result = await self.db.execute(
            select(User).where(User.email == user_data.email)
        )
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise BusinessRuleViolationException(
                "Email address already registered"
            )

        # Hash password
        password_hash = hash_password(user_data.password)

        # Create user
        user = User(
            email=user_data.email,
            password_hash=password_hash,
            full_name=user_data.full_name,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def authenticate_user(self, login_data: UserLogin) -> Dict[str, Any]:
        """Authenticate a user and generate access token.

        Args:
            login_data: User login credentials

        Returns:
            Dictionary containing access token and user info

        Raises:
            BusinessRuleViolationException: If credentials are invalid
        """
        # Find user by email
        result = await self.db.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise BusinessRuleViolationException(
                "Invalid email or password"
            )

        # Verify password
        if not verify_password(login_data.password, user.password_hash):
            raise BusinessRuleViolationException(
                "Invalid email or password"
            )

        # Generate access token
        token_data = {
            "user_id": str(user.id),
            "email": user.email,
        }

        expires_delta = timedelta(minutes=settings.access_token_expire_minutes)
        access_token = create_access_token(token_data, expires_delta)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.access_token_expire_minutes * 60,  # Convert to seconds
            "user": user,
        }

    async def get_user_by_id(self, user_id: UUID) -> User:
        """Get user by ID.

        Args:
            user_id: User ID

        Returns:
            User object

        Raises:
            BusinessRuleViolationException: If user not found
        """
        result = await self.db.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()

        if not user:
            raise BusinessRuleViolationException("User not found")

        return user
