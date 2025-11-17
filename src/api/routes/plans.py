"""API routes for fitness plans."""
from typing import Optional
from uuid import UUID
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, status, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession
from icalendar import Calendar, Event
from icalendar import vRecur

from src.core.database import get_db
from src.core.scheduler import get_scheduler
from src.api.middleware.auth import get_current_user
from src.services.plan_service import PlanService
from src.services.reminder_service import ReminderService
from src.services.exercise_service import ExerciseService
from src.api.schemas.plan_schemas import (
    FitnessPlanCreate,
    FitnessPlanUpdate,
    FitnessPlanDetail,
    FitnessPlanSummary,
    PaginatedPlansResponse,
    PaginationMeta,
    ExerciseCreate,
    ExerciseUpdate,
    ExerciseResponse,
)
from src.api.schemas.reminder_schemas import (
    ReminderCreate,
    ReminderUpdate,
    ReminderResponse,
)
from src.models.fitness_plan import PlanStatus
from src.models.reminder import ReminderFrequency
from src.core.config import settings
import math


router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("/", response_model=FitnessPlanDetail, status_code=status.HTTP_201_CREATED)
async def create_fitness_plan(
    plan_data: FitnessPlanCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new fitness plan.

    Args:
        plan_data: Plan creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created fitness plan
    """
    service = PlanService(db)
    plan = await service.create_plan(UUID(current_user["user_id"]), plan_data)

    # Build response with exercise count
    return FitnessPlanDetail(
        id=plan.id,
        name=plan.name,
        description=plan.description,
        status=plan.status.value,
        exercises=plan.exercises,
        reminders=[ReminderResponse.from_orm_model(r) for r in plan.reminders],
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.get("/", response_model=PaginatedPlansResponse)
async def list_fitness_plans(
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by plan status"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(settings.default_page_size, ge=1, le=settings.max_page_size, description="Items per page"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get paginated list of user's fitness plans.

    Args:
        status_filter: Optional filter by plan status
        page: Page number (1-based)
        page_size: Number of items per page
        current_user: Current authenticated user
        db: Database session

    Returns:
        Paginated list of plans
    """
    service = PlanService(db)

    # Parse status filter
    status_enum = None
    if status_filter:
        try:
            status_enum = PlanStatus(status_filter)
        except ValueError:
            pass

    plans, total_count = await service.get_user_plans(
        UUID(current_user["user_id"]), status=status_enum, page=page, page_size=page_size
    )

    # Build summary responses
    user_id = UUID(current_user["user_id"])
    plan_summaries = [
        FitnessPlanSummary(
            id=plan.id,
            name=plan.name,
            description=plan.description,
            status=plan.status.value,
            exercise_count=len(plan.exercises),
            is_owner=(plan.user_id == user_id),
            owner_email=plan.user.email if plan.user else None,
            created_at=plan.created_at,
            updated_at=plan.updated_at,
        )
        for plan in plans
    ]

    # Calculate pagination metadata
    total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0

    return PaginatedPlansResponse(
        plans=plan_summaries,
        pagination=PaginationMeta(
            page=page, page_size=page_size, total_items=total_count, total_pages=total_pages
        ),
    )


@router.get("/{plan_id}", response_model=FitnessPlanDetail)
async def get_fitness_plan(
    plan_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get detailed information about a specific fitness plan.

    Args:
        plan_id: ID of the plan
        current_user: Current authenticated user
        db: Database session

    Returns:
        Fitness plan details
    """
    service = PlanService(db)
    plan = await service.get_plan_by_id(UUID(current_user["user_id"]), plan_id)

    return FitnessPlanDetail(
        id=plan.id,
        name=plan.name,
        description=plan.description,
        status=plan.status.value,
        exercises=plan.exercises,
        reminders=[ReminderResponse.from_orm_model(r) for r in plan.reminders],
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.put("/{plan_id}", response_model=FitnessPlanDetail)
async def update_fitness_plan(
    plan_id: UUID,
    plan_data: FitnessPlanUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a fitness plan's basic information.

    Args:
        plan_id: ID of the plan
        plan_data: Updated plan data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated fitness plan
    """
    service = PlanService(db)
    plan = await service.update_plan(UUID(current_user["user_id"]), plan_id, plan_data)

    return FitnessPlanDetail(
        id=plan.id,
        name=plan.name,
        description=plan.description,
        status=plan.status.value,
        exercises=plan.exercises,
        reminders=[ReminderResponse.from_orm_model(r) for r in plan.reminders],
        created_at=plan.created_at,
        updated_at=plan.updated_at,
    )


@router.delete("/{plan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fitness_plan(
    plan_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a fitness plan (soft delete) and cancel all its reminders.

    Args:
        plan_id: ID of the plan
        current_user: Current authenticated user
        db: Database session
    """
    scheduler = get_scheduler()
    service = PlanService(db)
    await service.delete_plan(UUID(current_user["user_id"]), plan_id, scheduler)


# ========== Exercise Endpoints ==========


@router.post(
    "/{plan_id}/exercises/",
    response_model=ExerciseResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_exercise_to_plan(
    plan_id: UUID,
    exercise_data: ExerciseCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Add a new exercise to a fitness plan.

    Args:
        plan_id: ID of the plan
        exercise_data: Exercise data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created exercise
    """
    service = ExerciseService(db)
    exercise = await service.add_exercise(
        UUID(current_user["user_id"]), plan_id, exercise_data
    )

    return ExerciseResponse.model_validate(exercise)


@router.put("/{plan_id}/exercises/{exercise_id}", response_model=ExerciseResponse)
async def update_exercise(
    plan_id: UUID,
    exercise_id: UUID,
    exercise_data: ExerciseUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing exercise.

    Args:
        plan_id: ID of the plan
        exercise_id: ID of the exercise
        exercise_data: Updated exercise data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated exercise
    """
    service = ExerciseService(db)
    exercise = await service.update_exercise(
        UUID(current_user["user_id"]), plan_id, exercise_id, exercise_data
    )

    return ExerciseResponse.model_validate(exercise)


@router.delete(
    "/{plan_id}/exercises/{exercise_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_exercise(
    plan_id: UUID,
    exercise_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete an exercise from a fitness plan.

    Args:
        plan_id: ID of the plan
        exercise_id: ID of the exercise
        current_user: Current authenticated user
        db: Database session
    """
    service = ExerciseService(db)
    await service.delete_exercise(UUID(current_user["user_id"]), plan_id, exercise_id)


# ========== Reminder Endpoints ==========


@router.post(
    "/{plan_id}/reminders/",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_reminder(
    plan_id: UUID,
    reminder_data: ReminderCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new reminder for a fitness plan.

    Args:
        plan_id: ID of the plan
        reminder_data: Reminder creation data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created reminder
    """
    scheduler = get_scheduler()
    service = ReminderService(db, scheduler)
    reminder = await service.create_reminder(
        UUID(current_user["user_id"]), plan_id, reminder_data
    )

    return ReminderResponse.from_orm_model(reminder)


@router.put("/{plan_id}/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    plan_id: UUID,
    reminder_id: UUID,
    reminder_data: ReminderUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update an existing reminder.

    Args:
        plan_id: ID of the plan
        reminder_id: ID of the reminder
        reminder_data: Updated reminder data
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated reminder
    """
    scheduler = get_scheduler()
    service = ReminderService(db, scheduler)
    reminder = await service.update_reminder(
        UUID(current_user["user_id"]), plan_id, reminder_id, reminder_data
    )

    return ReminderResponse.from_orm_model(reminder)


@router.delete(
    "/{plan_id}/reminders/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_reminder(
    plan_id: UUID,
    reminder_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a reminder.

    Args:
        plan_id: ID of the plan
        reminder_id: ID of the reminder
        current_user: Current authenticated user
        db: Database session
    """
    scheduler = get_scheduler()
    service = ReminderService(db, scheduler)
    await service.delete_reminder(UUID(current_user["user_id"]), plan_id, reminder_id)


# ========== Calendar Export Endpoint ==========


@router.get("/{plan_id}/export/calendar")
async def export_plan_calendar(
    plan_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Export fitness plan reminders as an iCalendar (.ics) file.

    Args:
        plan_id: ID of the plan
        current_user: Current authenticated user
        db: Database session

    Returns:
        iCalendar file for download
    """
    # Get plan details
    plan_service = PlanService(db)
    plan = await plan_service.get_plan_by_id(UUID(current_user["user_id"]), plan_id)

    # Get reminders
    reminder_service = ReminderService(db)
    reminders = await reminder_service.get_plan_reminders(
        UUID(current_user["user_id"]), plan_id
    )

    # Create calendar
    cal = Calendar()
    cal.add("prodid", "-//Fitness Plan Reminder//mxm.dk//")
    cal.add("version", "2.0")
    cal.add("x-wr-calname", f"{plan.name} - 健身计划提醒")
    cal.add("x-wr-timezone", "Asia/Shanghai")

    # Add events for each reminder
    for reminder in reminders:
        if not reminder.is_enabled:
            continue

        event = Event()
        event.add("summary", f"🏋️ {plan.name}")

        # Build description with exercises
        exercise_list = "\n".join([
            f"- {ex.name} ({ex.duration_minutes}分钟)" if ex.duration_minutes
            else f"- {ex.name} ({ex.repetitions}次)"
            for ex in plan.exercises
        ])
        event.add("description", f"健身计划提醒\n\n锻炼项目：\n{exercise_list}")

        # Set start time (today at reminder time)
        now = datetime.now()
        start_time = datetime.combine(now.date(), reminder.reminder_time)
        event.add("dtstart", start_time)
        event.add("dtend", start_time + timedelta(hours=1))

        # Add recurrence rule based on frequency
        if reminder.frequency == ReminderFrequency.DAILY:
            event.add("rrule", {"freq": "daily"})
        elif reminder.frequency == ReminderFrequency.WEEKLY and reminder.days_of_week:
            # Convert days (1=Monday, 7=Sunday) to iCalendar format
            # iCalendar uses: MO, TU, WE, TH, FR, SA, SU
            day_map = {1: "MO", 2: "TU", 3: "WE", 4: "TH", 5: "FR", 6: "SA", 7: "SU"}
            byday = [day_map[day] for day in reminder.days_of_week if day in day_map]
            event.add("rrule", {"freq": "weekly", "byday": byday})
        elif reminder.frequency == ReminderFrequency.CUSTOM and reminder.days_of_week:
            # Same as weekly
            day_map = {1: "MO", 2: "TU", 3: "WE", 4: "TH", 5: "FR", 6: "SA", 7: "SU"}
            byday = [day_map[day] for day in reminder.days_of_week if day in day_map]
            event.add("rrule", {"freq": "weekly", "byday": byday})

        # Add unique ID
        event.add("uid", f"{plan_id}-{reminder.id}@fitness-plan")

        # Add alarm (15 minutes before)
        from icalendar import Alarm
        alarm = Alarm()
        alarm.add("action", "DISPLAY")
        alarm.add("description", f"健身提醒: {plan.name}")
        alarm.add("trigger", timedelta(minutes=-15))
        event.add_component(alarm)

        cal.add_component(event)

    # Return as downloadable file
    ics_content = cal.to_ical()
    # Use ASCII-safe filename and RFC 5987 encoding for Chinese characters
    from urllib.parse import quote
    safe_filename = "fitness_plan_calendar.ics"
    encoded_filename = quote(f"{plan.name}_calendar.ics".encode('utf-8'))

    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_filename}"; filename*=UTF-8\'\'{encoded_filename}'
        },
    )
