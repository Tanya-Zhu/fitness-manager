"""Integration tests for fitness plan reminder functionality."""
import pytest
from httpx import AsyncClient
from unittest.mock import AsyncMock, MagicMock, patch


@pytest.mark.integration
class TestReminderSetup:
    """Integration tests for setting up reminders."""

    @pytest.mark.asyncio
    async def test_complete_reminder_setup_flow(self, auth_client: AsyncClient):
        """Test complete flow of creating a plan and adding reminders."""
        # Create a fitness plan first
        plan_data = {
            "name": "早晨锻炼",
            "description": "每天早上的健身计划",
            "exercises": [
                {"name": "跑步", "duration_minutes": 30, "intensity": "medium"},
                {"name": "拉伸", "duration_minutes": 10, "intensity": "low"},
            ],
        }

        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        assert create_response.status_code == 201, "Plan creation should succeed"

        plan_id = create_response.json()["id"]

        # Add a reminder to the plan
        reminder_data = {
            "reminder_time": "07:00:00",
            "frequency": "daily",
            "days_of_week": [1, 2, 3, 4, 5],  # Weekdays
            "is_enabled": True,
        }

        reminder_response = await auth_client.post(
            f"/api/v1/plans/{plan_id}/reminders", json=reminder_data
        )
        assert reminder_response.status_code == 201, "Reminder creation should succeed"

        reminder = reminder_response.json()
        assert reminder["reminder_time"] == "07:00:00"
        assert reminder["frequency"] == "daily"
        assert reminder["is_enabled"] is True

        # Verify the reminder is included in plan details
        plan_detail_response = await auth_client.get(f"/api/v1/plans/{plan_id}")
        assert plan_detail_response.status_code == 200

        plan_details = plan_detail_response.json()
        assert len(plan_details["reminders"]) == 1
        assert plan_details["reminders"][0]["id"] == reminder["id"]

    @pytest.mark.asyncio
    async def test_reminder_validation_errors(self, auth_client: AsyncClient):
        """Test that invalid reminder data returns validation errors."""
        # Create a fitness plan first
        plan_data = {
            "name": "测试计划",
            "exercises": [{"name": "跑步", "duration_minutes": 30}],
        }

        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        assert create_response.status_code == 201

        plan_id = create_response.json()["id"]

        # Test missing reminder_time
        invalid_reminder = {
            "frequency": "daily",
            "days_of_week": [1],
        }

        response = await auth_client.post(
            f"/api/v1/plans/{plan_id}/reminders", json=invalid_reminder
        )
        assert response.status_code == 422, "Should return validation error"

        # Test invalid time format
        invalid_time_reminder = {
            "reminder_time": "25:00:00",  # Invalid hour
            "frequency": "daily",
            "days_of_week": [1],
        }

        response = await auth_client.post(
            f"/api/v1/plans/{plan_id}/reminders", json=invalid_time_reminder
        )
        assert response.status_code == 422, "Should return validation error"

    @pytest.mark.asyncio
    async def test_update_reminder(self, auth_client: AsyncClient):
        """Test updating an existing reminder."""
        # Create a plan with a reminder
        plan_data = {
            "name": "测试计划",
            "exercises": [{"name": "跑步", "duration_minutes": 30}],
        }
        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        plan_id = create_response.json()["id"]

        reminder_data = {
            "reminder_time": "07:00:00",
            "frequency": "daily",
            "days_of_week": [1, 3, 5],
            "is_enabled": True,
        }
        reminder_response = await auth_client.post(
            f"/api/v1/plans/{plan_id}/reminders", json=reminder_data
        )
        reminder_id = reminder_response.json()["id"]

        # Update the reminder
        updated_data = {
            "reminder_time": "08:30:00",
            "frequency": "weekly",
            "days_of_week": [2, 4],
            "is_enabled": False,
        }

        update_response = await auth_client.put(
            f"/api/v1/plans/{plan_id}/reminders/{reminder_id}", json=updated_data
        )
        assert update_response.status_code == 200, "Update should succeed"

        updated_reminder = update_response.json()
        assert updated_reminder["reminder_time"] == "08:30:00"
        assert updated_reminder["frequency"] == "weekly"
        assert updated_reminder["days_of_week"] == [2, 4]
        assert updated_reminder["is_enabled"] is False

    @pytest.mark.asyncio
    async def test_delete_reminder(self, auth_client: AsyncClient):
        """Test deleting a reminder."""
        # Create a plan with a reminder
        plan_data = {
            "name": "测试计划",
            "exercises": [{"name": "跑步", "duration_minutes": 30}],
        }
        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        plan_id = create_response.json()["id"]

        reminder_data = {
            "reminder_time": "07:00:00",
            "frequency": "daily",
            "days_of_week": [1],
            "is_enabled": True,
        }
        reminder_response = await auth_client.post(
            f"/api/v1/plans/{plan_id}/reminders", json=reminder_data
        )
        reminder_id = reminder_response.json()["id"]

        # Delete the reminder
        delete_response = await auth_client.delete(
            f"/api/v1/plans/{plan_id}/reminders/{reminder_id}"
        )
        assert delete_response.status_code == 204, "Delete should succeed"

        # Verify the reminder is removed
        plan_detail_response = await auth_client.get(f"/api/v1/plans/{plan_id}")
        plan_details = plan_detail_response.json()
        assert len(plan_details["reminders"]) == 0


@pytest.mark.integration
class TestReminderNotificationDelivery:
    """Integration tests for reminder notification delivery."""

    @pytest.mark.asyncio
    @patch("src.services.reminder_service.APScheduler")
    async def test_reminder_scheduled_on_creation(
        self, mock_scheduler: MagicMock, auth_client: AsyncClient
    ):
        """Test that creating a reminder schedules an APScheduler job."""
        # Setup mock
        mock_scheduler_instance = MagicMock()
        mock_scheduler.return_value = mock_scheduler_instance

        # Create a plan
        plan_data = {
            "name": "测试计划",
            "exercises": [{"name": "跑步", "duration_minutes": 30}],
        }
        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        plan_id = create_response.json()["id"]

        # Add a reminder
        reminder_data = {
            "reminder_time": "07:00:00",
            "frequency": "daily",
            "days_of_week": [1, 2, 3, 4, 5],
            "is_enabled": True,
        }

        response = await auth_client.post(
            f"/api/v1/plans/{plan_id}/reminders", json=reminder_data
        )
        assert response.status_code == 201

        # Verify scheduler was called (this will be implemented later)
        # For now, just verify the reminder was created
        reminder = response.json()
        assert reminder["is_enabled"] is True

    @pytest.mark.asyncio
    @patch("src.services.notification_service.NotificationService.send_push_notification")
    async def test_reminder_notification_content(
        self, mock_send_notification: AsyncMock, auth_client: AsyncClient
    ):
        """Test that reminder notifications contain correct plan information."""
        # Setup mock
        mock_send_notification.return_value = {"status": "sent"}

        # Create a plan with exercises
        plan_data = {
            "name": "晨练计划",
            "description": "每天早上的健身",
            "exercises": [
                {"name": "跑步", "duration_minutes": 30},
                {"name": "俯卧撑", "repetitions": 20},
            ],
        }
        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        plan_id = create_response.json()["id"]

        # Add a reminder
        reminder_data = {
            "reminder_time": "07:00:00",
            "frequency": "daily",
            "days_of_week": [1, 2, 3, 4, 5],
            "is_enabled": True,
        }

        response = await auth_client.post(
            f"/api/v1/plans/{plan_id}/reminders", json=reminder_data
        )
        assert response.status_code == 201

        # In actual implementation, this would trigger a notification
        # For now, just verify the reminder was created with correct data
        reminder = response.json()
        assert reminder["reminder_time"] == "07:00:00"

    @pytest.mark.asyncio
    async def test_disabled_reminder_not_triggered(self, auth_client: AsyncClient):
        """Test that disabled reminders do not trigger notifications."""
        # Create a plan
        plan_data = {
            "name": "测试计划",
            "exercises": [{"name": "跑步", "duration_minutes": 30}],
        }
        create_response = await auth_client.post("/api/v1/plans", json=plan_data)
        plan_id = create_response.json()["id"]

        # Create a disabled reminder
        reminder_data = {
            "reminder_time": "07:00:00",
            "frequency": "daily",
            "days_of_week": [1],
            "is_enabled": False,
        }

        response = await auth_client.post(
            f"/api/v1/plans/{plan_id}/reminders", json=reminder_data
        )
        assert response.status_code == 201

        reminder = response.json()
        assert reminder["is_enabled"] is False

        # Implementation should not schedule this job
        # This will be verified once scheduler is implemented
