"""API routes for plan execution tracking."""
from typing import Optional
from uuid import UUID
from datetime import date
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
import math

from src.core.database import get_db
from src.api.middleware.auth import get_current_user
from src.services.plan_execution_service import PlanExecutionService
from src.api.schemas.plan_execution_schemas import (
    PlanExecutionCreate,
    PlanExecutionUpdate,
    PlanExecutionResponse,
    PaginatedPlanExecutionsResponse,
    PaginationMeta,
)
from src.core.config import settings


router = APIRouter(prefix="/plan-executions", tags=["plan-executions"])


@router.post("/", response_model=PlanExecutionResponse, status_code=status.HTTP_201_CREATED)
async def create_plan_execution(
    execution_data: PlanExecutionCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new plan execution record.

    Args:
        execution_data: Plan execution creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created plan execution with exercise executions
    """
    service = PlanExecutionService(db)
    plan_execution = await service.create_plan_execution(
        UUID(current_user["user_id"]), execution_data
    )

    return PlanExecutionResponse.model_validate(plan_execution)


@router.get("/", response_model=PaginatedPlanExecutionsResponse)
async def list_plan_executions(
    plan_id: Optional[UUID] = Query(None, description="Filter by plan ID"),
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(
        settings.default_page_size,
        ge=1,
        le=settings.max_page_size,
        description="Items per page",
    ),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of user's plan executions.

    Args:
        plan_id: Optional plan ID filter
        start_date: Optional start date filter
        end_date: Optional end date filter
        page: Page number (1-based)
        page_size: Number of items per page
        current_user: Current authenticated user
        db: Database session

    Returns:
        Paginated list of plan executions with summary data
    """
    service = PlanExecutionService(db)

    # Get plan executions with summary
    plan_executions, total_count = await service.get_plan_executions(
        UUID(current_user["user_id"]),
        plan_id=plan_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )

    # Calculate pagination metadata
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0

    return PaginatedPlanExecutionsResponse(
        plan_executions=plan_executions,
        pagination=PaginationMeta(
            page=page, page_size=page_size, total_items=total_count, total_pages=total_pages
        ),
    )


@router.get("/{execution_id}", response_model=PlanExecutionResponse)
async def get_plan_execution(
    execution_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific plan execution.

    Args:
        execution_id: ID of the plan execution
        current_user: Current authenticated user
        db: Database session

    Returns:
        Plan execution details with all exercise executions
    """
    service = PlanExecutionService(db)
    plan_execution = await service.get_plan_execution_by_id(
        UUID(current_user["user_id"]), execution_id
    )

    return PlanExecutionResponse.model_validate(plan_execution)


@router.put("/{execution_id}", response_model=PlanExecutionResponse)
async def update_plan_execution(
    execution_id: UUID,
    execution_data: PlanExecutionUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a plan execution.

    Args:
        execution_id: ID of the plan execution
        execution_data: Updated plan execution data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated plan execution
    """
    service = PlanExecutionService(db)
    plan_execution = await service.update_plan_execution(
        UUID(current_user["user_id"]), execution_id, execution_data
    )

    return PlanExecutionResponse.model_validate(plan_execution)


@router.delete("/{execution_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_plan_execution(
    execution_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a plan execution.

    Args:
        execution_id: ID of the plan execution
        current_user: Current authenticated user
        db: Database session
    """
    service = PlanExecutionService(db)
    await service.delete_plan_execution(UUID(current_user["user_id"]), execution_id)
