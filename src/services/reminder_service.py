"""Service for managing fitness plan reminders."""
from datetime import time
from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from src.models.reminder import Reminder, ReminderFrequency
from src.models.fitness_plan import FitnessPlan
from src.api.schemas.reminder_schemas import ReminderCreate, ReminderUpdate
from src.api.middleware.error_handler import NotFoundException, BusinessRuleViolationException
from src.services.notification_service import NotificationService


class ReminderService:
    """Service for managing reminders."""

    def __init__(self, db: AsyncSession, scheduler: Optional[AsyncIOScheduler] = None):
        """Initialize reminder service.

        Args:
            db: Database session
            scheduler: APScheduler instance (optional for testing)
        """
        self.db = db
        self.scheduler = scheduler

    async def create_reminder(
        self, user_id: UUID, plan_id: UUID, reminder_data: ReminderCreate
    ) -> Reminder:
        """Create a new reminder for a fitness plan.

        Args:
            user_id: User ID (for ownership verification)
            plan_id: Plan ID to attach reminder to
            reminder_data: Reminder creation data

        Returns:
            Created reminder

        Raises:
            NotFoundException: If plan not found or not owned by user
        """
        # Verify plan exists and belongs to user
        result = await self.db.execute(
            select(FitnessPlan).where(
                and_(
                    FitnessPlan.id == plan_id,
                    FitnessPlan.user_id == user_id,
                    FitnessPlan.deleted_at.is_(None),
                )
            )
        )
        plan = result.scalar_one_or_none()

        if plan is None:
            raise NotFoundException("Fitness plan not found")

        # Create reminder
        reminder = Reminder(
            plan_id=plan_id,
            reminder_time=reminder_data.reminder_time,
            frequency=reminder_data.frequency,
            days_of_week=reminder_data.days_of_week,
            is_enabled=reminder_data.is_enabled,
        )

        self.db.add(reminder)
        await self.db.flush()

        # Schedule job if enabled
        if reminder.is_enabled and self.scheduler:
            await self._schedule_job(reminder, plan)

        await self.db.commit()
        await self.db.refresh(reminder)

        return reminder

    async def update_reminder(
        self, user_id: UUID, plan_id: UUID, reminder_id: UUID, reminder_data: ReminderUpdate
    ) -> Reminder:
        """Update an existing reminder.

        Args:
            user_id: User ID (for ownership verification)
            plan_id: Plan ID
            reminder_id: Reminder ID to update
            reminder_data: Updated reminder data

        Returns:
            Updated reminder

        Raises:
            NotFoundException: If reminder not found or not owned by user
        """
        # Fetch reminder with plan ownership verification
        result = await self.db.execute(
            select(Reminder)
            .join(FitnessPlan, Reminder.plan_id == FitnessPlan.id)
            .where(
                and_(
                    Reminder.id == reminder_id,
                    Reminder.plan_id == plan_id,
                    FitnessPlan.user_id == user_id,
                    FitnessPlan.deleted_at.is_(None),
                )
            )
        )
        reminder = result.scalar_one_or_none()

        if reminder is None:
            raise NotFoundException("Reminder not found")

        # Update fields
        update_data = reminder_data.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(reminder, field, value)

        await self.db.flush()

        # Reschedule job if scheduler is available
        if self.scheduler:
            # Remove old job
            job_id = self._get_job_id(plan_id, reminder_id)
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

            # Schedule new job if enabled
            if reminder.is_enabled:
                # Fetch plan for scheduling
                plan_result = await self.db.execute(
                    select(FitnessPlan).where(FitnessPlan.id == plan_id)
                )
                plan = plan_result.scalar_one()
                await self._schedule_job(reminder, plan)

        await self.db.commit()
        await self.db.refresh(reminder)

        return reminder

    async def delete_reminder(
        self, user_id: UUID, plan_id: UUID, reminder_id: UUID
    ) -> None:
        """Delete a reminder.

        Args:
            user_id: User ID (for ownership verification)
            plan_id: Plan ID
            reminder_id: Reminder ID to delete

        Raises:
            NotFoundException: If reminder not found or not owned by user
        """
        # Fetch reminder with plan ownership verification
        result = await self.db.execute(
            select(Reminder)
            .join(FitnessPlan, Reminder.plan_id == FitnessPlan.id)
            .where(
                and_(
                    Reminder.id == reminder_id,
                    Reminder.plan_id == plan_id,
                    FitnessPlan.user_id == user_id,
                    FitnessPlan.deleted_at.is_(None),
                )
            )
        )
        reminder = result.scalar_one_or_none()

        if reminder is None:
            raise NotFoundException("Reminder not found")

        # Remove scheduled job if exists
        if self.scheduler:
            job_id = self._get_job_id(plan_id, reminder_id)
            if self.scheduler.get_job(job_id):
                self.scheduler.remove_job(job_id)

        # Delete reminder
        await self.db.delete(reminder)
        await self.db.commit()

    async def get_plan_reminders(
        self, user_id: UUID, plan_id: UUID
    ) -> List[Reminder]:
        """Get all reminders for a plan.

        Args:
            user_id: User ID (for ownership verification)
            plan_id: Plan ID

        Returns:
            List of reminders

        Raises:
            NotFoundException: If plan not found or not owned by user
        """
        # Verify plan exists and belongs to user
        result = await self.db.execute(
            select(FitnessPlan).where(
                and_(
                    FitnessPlan.id == plan_id,
                    FitnessPlan.user_id == user_id,
                    FitnessPlan.deleted_at.is_(None),
                )
            )
        )
        plan = result.scalar_one_or_none()

        if plan is None:
            raise NotFoundException("Fitness plan not found")

        # Fetch reminders
        result = await self.db.execute(
            select(Reminder).where(Reminder.plan_id == plan_id)
        )
        reminders = result.scalars().all()

        return list(reminders)

    async def _schedule_job(self, reminder: Reminder, plan: FitnessPlan) -> None:
        """Schedule an APScheduler job for a reminder.

        Args:
            reminder: Reminder to schedule
            plan: Associated fitness plan
        """
        if not self.scheduler:
            return

        job_id = self._get_job_id(plan.id, reminder.id)
        trigger = self._create_cron_trigger(
            reminder.reminder_time, reminder.frequency, reminder.days_of_week
        )

        # Schedule job
        self.scheduler.add_job(
            send_reminder_notification,
            trigger=trigger,
            id=job_id,
            args=[str(plan.id), str(reminder.id)],
            replace_existing=True,
            misfire_grace_time=300,  # 5 minutes
        )

    def _create_cron_trigger(
        self, reminder_time: time, frequency: ReminderFrequency, days_of_week: Optional[List[int]]
    ) -> CronTrigger:
        """Create a CronTrigger from reminder settings.

        Args:
            reminder_time: Time to trigger (HH:MM:SS)
            frequency: Reminder frequency
            days_of_week: Days of week (1-7) for weekly/custom

        Returns:
            CronTrigger instance
        """
        hour = reminder_time.hour
        minute = reminder_time.minute
        second = reminder_time.second

        if frequency == ReminderFrequency.DAILY:
            # Every day at the specified time
            return CronTrigger(hour=hour, minute=minute, second=second)
        elif frequency == ReminderFrequency.WEEKLY and days_of_week:
            # Specific days of week (convert 1-7 to 0-6 for cron)
            cron_days = ",".join(str((day - 1) % 7) for day in days_of_week)
            return CronTrigger(
                day_of_week=cron_days, hour=hour, minute=minute, second=second
            )
        elif frequency == ReminderFrequency.CUSTOM and days_of_week:
            # Custom days of week
            cron_days = ",".join(str((day - 1) % 7) for day in days_of_week)
            return CronTrigger(
                day_of_week=cron_days, hour=hour, minute=minute, second=second
            )
        else:
            # Default to daily if no valid configuration
            return CronTrigger(hour=hour, minute=minute, second=second)

    @staticmethod
    def _get_job_id(plan_id: UUID, reminder_id: UUID) -> str:
        """Generate APScheduler job ID for a reminder.

        Args:
            plan_id: Plan ID
            reminder_id: Reminder ID

        Returns:
            Job ID string
        """
        return f"reminder_{plan_id}_{reminder_id}"


# Callback function for sending reminder notifications
async def send_reminder_notification(plan_id_str: str, reminder_id_str: str) -> None:
    """Callback function executed by APScheduler to send reminder notification.

    This function is called by APScheduler at the scheduled time.
    It fetches the plan details and sends a notification.

    Args:
        plan_id_str: Plan ID as string
        reminder_id_str: Reminder ID as string
    """
    from src.core.database import AsyncSessionLocal
    from uuid import UUID

    plan_id = UUID(plan_id_str)
    reminder_id = UUID(reminder_id_str)

    async with AsyncSessionLocal() as db:
        # Fetch plan and reminder
        result = await db.execute(
            select(FitnessPlan)
            .where(
                and_(
                    FitnessPlan.id == plan_id,
                    FitnessPlan.deleted_at.is_(None),
                )
            )
        )
        plan = result.scalar_one_or_none()

        if not plan:
            return  # Plan deleted or not found

        # Check if plan is active (don't send reminders for paused plans)
        if plan.status != "active":
            return

        # Fetch reminder to check if it's still enabled
        reminder_result = await db.execute(
            select(Reminder).where(Reminder.id == reminder_id)
        )
        reminder = reminder_result.scalar_one_or_none()

        if not reminder or not reminder.is_enabled:
            return  # Reminder deleted or disabled

        # Send notification
        notification_service = NotificationService()
        await notification_service.send_push_notification(
            user_id=plan.user_id,
            plan_id=plan.id,
            plan_name=plan.name,
            exercises=plan.exercises,
        )
