"""Health check endpoint."""
from fastapi import APIRouter, status
from pydantic import BaseModel


router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str


@router.get("/health", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check() -> HealthResponse:
    """Health check endpoint.

    Returns:
        Health status and API version
    """
    return HealthResponse(status="healthy", version="0.1.0")
