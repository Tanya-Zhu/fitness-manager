"""Unified error response handler."""
from typing import Any, Dict
from fastapi import Request, status
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError


class AppException(Exception):
    """Base application exception."""

    def __init__(self, detail: str, code: str, status_code: int = status.HTTP_400_BAD_REQUEST):
        self.detail = detail
        self.code = code
        self.status_code = status_code
        super().__init__(self.detail)


class NotFoundException(AppException):
    """Resource not found exception."""

    def __init__(self, detail: str = "Resource not found"):
        super().__init__(detail, "NOT_FOUND", status.HTTP_404_NOT_FOUND)


class BusinessRuleViolationException(AppException):
    """Business rule violation exception."""

    def __init__(self, detail: str):
        super().__init__(detail, "BUSINESS_RULE_VIOLATION", status.HTTP_400_BAD_REQUEST)


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    """Handle application-specific exceptions.

    Args:
        request: FastAPI request object
        exc: Application exception

    Returns:
        JSON response with error details
    """
    return JSONResponse(
        status_code=exc.status_code, content={"detail": exc.detail, "code": exc.code}
    )


async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError) -> JSONResponse:
    """Handle SQLAlchemy database exceptions.

    Args:
        request: FastAPI request object
        exc: SQLAlchemy exception

    Returns:
        JSON response with generic database error
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Database error occurred", "code": "DATABASE_ERROR"},
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle unexpected exceptions.

    Args:
        request: FastAPI request object
        exc: Generic exception

    Returns:
        JSON response with generic error message
    """
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error", "code": "INTERNAL_ERROR"},
    )
