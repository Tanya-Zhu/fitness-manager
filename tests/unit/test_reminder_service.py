"""Unit tests for ReminderService."""
import pytest
from uuid import uuid4
from datetime import time
from unittest.mock import MagicMock, AsyncMock
from src.services.reminder_service import ReminderService
from src.api.schemas.reminder_schemas import ReminderCreate, ReminderUpdate, ReminderFrequency
from src.api.middleware.error_handler import NotFoundException
from src.models.reminder import Reminder
from src.models.fitness_plan import FitnessPlan


@pytest.mark.unit
class TestReminderServiceCreate:
    """Unit tests for creating reminders."""

    @pytest.mark.asyncio
    async def test_create_reminder_success(self, db_session):
        """Test successful reminder creation."""
        service = ReminderService(db_session)
        user_id = uuid4()

        # Create a plan first
        plan = FitnessPlan(
            id=uuid4(), user_id=user_id, name="Test Plan", status="active"
        )
        db_session.add(plan)
        await db_session.commit()

        # Create reminder
        reminder_data = ReminderCreate(
            reminder_time=time(7, 30, 0),
            frequency=ReminderFrequency.DAILY,
            days_of_week=[1, 2, 3, 4, 5],
            is_enabled=True,
        )

        reminder = await service.create_reminder(user_id, plan.id, reminder_data)

        assert reminder.id is not None
        assert reminder.plan_id == plan.id
        assert reminder.reminder_time == time(7, 30, 0)
        assert reminder.frequency == ReminderFrequency.DAILY
        assert reminder.days_of_week == [1, 2, 3, 4, 5]
        assert reminder.is_enabled is True

    @pytest.mark.asyncio
    async def test_create_reminder_plan_not_found(self, db_session):
        """Test creating reminder for non-existent plan raises NotFoundException."""
        service = ReminderService(db_session)
        user_id = uuid4()
        non_existent_plan_id = uuid4()

        reminder_data = ReminderCreate(
            reminder_time=time(7, 30, 0),
            frequency=ReminderFrequency.DAILY,
            days_of_week=[1],
            is_enabled=True,
        )

        with pytest.raises(NotFoundException):
            await service.create_reminder(user_id, non_existent_plan_id, reminder_data)

    @pytest.mark.asyncio
    async def test_create_reminder_wrong_user(self, db_session):
        """Test creating reminder for another user's plan raises NotFoundException."""
        service = ReminderService(db_session)
        owner_id = uuid4()
        other_user_id = uuid4()

        # Create a plan owned by owner_id
        plan = FitnessPlan(
            id=uuid4(), user_id=owner_id, name="Owner Plan", status="active"
        )
        db_session.add(plan)
        await db_session.commit()

        # Try to create reminder as different user
        reminder_data = ReminderCreate(
            reminder_time=time(7, 30, 0),
            frequency=ReminderFrequency.DAILY,
            days_of_week=[1],
            is_enabled=True,
        )

        with pytest.raises(NotFoundException):
            await service.create_reminder(other_user_id, plan.id, reminder_data)


@pytest.mark.unit
class TestReminderServiceUpdate:
    """Unit tests for updating reminders."""

    @pytest.mark.asyncio
    async def test_update_reminder_success(self, db_session):
        """Test successful reminder update."""
        service = ReminderService(db_session)
        user_id = uuid4()

        # Create a plan and reminder
        plan = FitnessPlan(
            id=uuid4(), user_id=user_id, name="Test Plan", status="active"
        )
        db_session.add(plan)
        await db_session.flush()

        reminder = Reminder(
            plan_id=plan.id,
            reminder_time=time(7, 0, 0),
            frequency=ReminderFrequency.DAILY,
            days_of_week=[1, 3, 5],
            is_enabled=True,
        )
        db_session.add(reminder)
        await db_session.commit()

        # Update reminder
        update_data = ReminderUpdate(
            reminder_time=time(8, 30, 0),
            frequency=ReminderFrequency.WEEKLY,
            days_of_week=[2, 4],
            is_enabled=False,
        )

        updated_reminder = await service.update_reminder(
            user_id, plan.id, reminder.id, update_data
        )

        assert updated_reminder.reminder_time == time(8, 30, 0)
        assert updated_reminder.frequency == ReminderFrequency.WEEKLY
        assert updated_reminder.days_of_week == [2, 4]
        assert updated_reminder.is_enabled is False

    @pytest.mark.asyncio
    async def test_update_reminder_partial(self, db_session):
        """Test partial reminder update."""
        service = ReminderService(db_session)
        user_id = uuid4()

        # Create a plan and reminder
        plan = FitnessPlan(
            id=uuid4(), user_id=user_id, name="Test Plan", status="active"
        )
        db_session.add(plan)
        await db_session.flush()

        reminder = Reminder(
            plan_id=plan.id,
            reminder_time=time(7, 0, 0),
            frequency=ReminderFrequency.DAILY,
            days_of_week=[1, 3, 5],
            is_enabled=True,
        )
        db_session.add(reminder)
        await db_session.commit()

        # Update only is_enabled
        update_data = ReminderUpdate(is_enabled=False)

        updated_reminder = await service.update_reminder(
            user_id, plan.id, reminder.id, update_data
        )

        # Only is_enabled should change
        assert updated_reminder.reminder_time == time(7, 0, 0)
        assert updated_reminder.frequency == ReminderFrequency.DAILY
        assert updated_reminder.days_of_week == [1, 3, 5]
        assert updated_reminder.is_enabled is False

    @pytest.mark.asyncio
    async def test_update_reminder_not_found(self, db_session):
        """Test updating non-existent reminder raises NotFoundException."""
        service = ReminderService(db_session)
        user_id = uuid4()
        plan_id = uuid4()
        reminder_id = uuid4()

        update_data = ReminderUpdate(is_enabled=False)

        with pytest.raises(NotFoundException):
            await service.update_reminder(user_id, plan_id, reminder_id, update_data)


@pytest.mark.unit
class TestReminderServiceDelete:
    """Unit tests for deleting reminders."""

    @pytest.mark.asyncio
    async def test_delete_reminder_success(self, db_session):
        """Test successful reminder deletion."""
        service = ReminderService(db_session)
        user_id = uuid4()

        # Create a plan and reminder
        plan = FitnessPlan(
            id=uuid4(), user_id=user_id, name="Test Plan", status="active"
        )
        db_session.add(plan)
        await db_session.flush()

        reminder = Reminder(
            plan_id=plan.id,
            reminder_time=time(7, 0, 0),
            frequency=ReminderFrequency.DAILY,
            days_of_week=[1],
            is_enabled=True,
        )
        db_session.add(reminder)
        await db_session.commit()

        reminder_id = reminder.id

        # Delete reminder
        await service.delete_reminder(user_id, plan.id, reminder_id)

        # Verify deletion
        from sqlalchemy import select

        result = await db_session.execute(
            select(Reminder).where(Reminder.id == reminder_id)
        )
        deleted_reminder = result.scalar_one_or_none()

        assert deleted_reminder is None

    @pytest.mark.asyncio
    async def test_delete_reminder_not_found(self, db_session):
        """Test deleting non-existent reminder raises NotFoundException."""
        service = ReminderService(db_session)
        user_id = uuid4()
        plan_id = uuid4()
        reminder_id = uuid4()

        with pytest.raises(NotFoundException):
            await service.delete_reminder(user_id, plan_id, reminder_id)


@pytest.mark.unit
class TestReminderServiceScheduling:
    """Unit tests for reminder scheduling logic."""

    def test_create_cron_trigger_daily(self):
        """Test creating cron trigger for daily reminders."""
        service = ReminderService(None)

        trigger = service._create_cron_trigger(
            time(7, 30, 0), ReminderFrequency.DAILY, None
        )

        assert trigger.fields[2].expressions[0].first == 7  # hour
        assert trigger.fields[3].expressions[0].first == 30  # minute

    def test_create_cron_trigger_weekly(self):
        """Test creating cron trigger for weekly reminders."""
        service = ReminderService(None)

        # Monday, Wednesday, Friday (1, 3, 5) -> (0, 2, 4) in cron
        trigger = service._create_cron_trigger(
            time(8, 0, 0), ReminderFrequency.WEEKLY, [1, 3, 5]
        )

        assert trigger.fields[2].expressions[0].first == 8  # hour
        assert trigger.fields[3].expressions[0].first == 0  # minute

    def test_get_job_id_format(self):
        """Test job ID format generation."""
        plan_id = uuid4()
        reminder_id = uuid4()

        job_id = ReminderService._get_job_id(plan_id, reminder_id)

        assert job_id == f"reminder_{plan_id}_{reminder_id}"
        assert job_id.startswith("reminder_")
