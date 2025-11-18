"""Unit tests for NotificationService."""
import pytest
from uuid import uuid4
from unittest.mock import MagicMock
from src.services.notification_service import NotificationService


@pytest.mark.unit
class TestNotificationServiceFormatting:
    """Unit tests for notification message formatting."""

    @pytest.mark.asyncio
    async def test_format_message_with_duration(self):
        """Test formatting notification message with duration-based exercises."""
        service = NotificationService()

        # Create mock exercises
        exercise1 = MagicMock()
        exercise1.name = "跑步"
        exercise1.duration_minutes = 30
        exercise1.repetitions = None
        exercise1.intensity = MagicMock(value="medium")

        exercise2 = MagicMock()
        exercise2.name = "拉伸"
        exercise2.duration_minutes = 10
        exercise2.repetitions = None
        exercise2.intensity = MagicMock(value="low")

        exercises = [exercise1, exercise2]

        message = service._format_message("早晨锻炼", exercises)

        assert "早晨锻炼" in message
        assert "跑步" in message
        assert "30分钟" in message
        assert "拉伸" in message
        assert "10分钟" in message
        assert "中强度" in message
        assert "低强度" in message

    @pytest.mark.asyncio
    async def test_format_message_with_repetitions(self):
        """Test formatting notification message with repetition-based exercises."""
        service = NotificationService()

        # Create mock exercise
        exercise = MagicMock()
        exercise.name = "俯卧撑"
        exercise.duration_minutes = None
        exercise.repetitions = 20
        exercise.intensity = MagicMock(value="high")

        exercises = [exercise]

        message = service._format_message("力量训练", exercises)

        assert "力量训练" in message
        assert "俯卧撑" in message
        assert "20次" in message
        assert "高强度" in message

    @pytest.mark.asyncio
    async def test_format_message_empty_exercises(self):
        """Test formatting notification message with no exercises."""
        service = NotificationService()

        message = service._format_message("空计划", [])

        assert "空计划" in message
        assert "暂无锻炼项目" in message

    def test_create_exercise_summary_multiple_exercises(self):
        """Test creating exercise summary with multiple exercises."""
        service = NotificationService()

        # Create mock exercises
        exercise1 = MagicMock()
        exercise1.name = "跑步"
        exercise1.duration_minutes = 30
        exercise1.repetitions = None
        exercise1.intensity = MagicMock(value="medium")

        exercise2 = MagicMock()
        exercise2.name = "俯卧撑"
        exercise2.duration_minutes = None
        exercise2.repetitions = 20
        exercise2.intensity = MagicMock(value="high")

        exercises = [exercise1, exercise2]

        summary = service._create_exercise_summary(exercises)

        # Check structure
        lines = summary.split("\n")
        assert len(lines) == 2
        assert "1. 跑步" in lines[0]
        assert "30分钟" in lines[0]
        assert "2. 俯卧撑" in lines[1]
        assert "20次" in lines[1]

    def test_create_exercise_summary_intensity_mapping(self):
        """Test intensity level mapping in exercise summary."""
        service = NotificationService()

        # Test low intensity
        exercise_low = MagicMock()
        exercise_low.name = "散步"
        exercise_low.duration_minutes = 20
        exercise_low.repetitions = None
        exercise_low.intensity = MagicMock(value="low")

        summary = service._create_exercise_summary([exercise_low])
        assert "低强度" in summary

        # Test medium intensity
        exercise_medium = MagicMock()
        exercise_medium.name = "慢跑"
        exercise_medium.duration_minutes = 25
        exercise_medium.repetitions = None
        exercise_medium.intensity = MagicMock(value="medium")

        summary = service._create_exercise_summary([exercise_medium])
        assert "中强度" in summary

        # Test high intensity
        exercise_high = MagicMock()
        exercise_high.name = "冲刺"
        exercise_high.duration_minutes = 10
        exercise_high.repetitions = None
        exercise_high.intensity = MagicMock(value="high")

        summary = service._create_exercise_summary([exercise_high])
        assert "高强度" in summary


@pytest.mark.unit
class TestNotificationServiceSending:
    """Unit tests for sending notifications."""

    @pytest.mark.asyncio
    async def test_send_push_notification(self):
        """Test sending a push notification."""
        service = NotificationService()
        user_id = uuid4()
        plan_id = uuid4()

        # Create mock exercises
        exercise = MagicMock()
        exercise.name = "跑步"
        exercise.duration_minutes = 30
        exercise.repetitions = None
        exercise.intensity = MagicMock(value="medium")

        result = await service.send_push_notification(
            user_id=user_id,
            plan_id=plan_id,
            plan_name="晨跑计划",
            exercises=[exercise],
        )

        assert result["status"] == "sent"
        assert result["user_id"] == str(user_id)
        assert result["plan_id"] == str(plan_id)
        assert "message" in result
        assert "晨跑计划" in result["message"]

    @pytest.mark.asyncio
    async def test_send_bulk_notifications(self):
        """Test sending multiple notifications in bulk."""
        service = NotificationService()

        # Create mock exercise
        exercise = MagicMock()
        exercise.name = "跑步"
        exercise.duration_minutes = 30
        exercise.repetitions = None
        exercise.intensity = MagicMock(value="medium")

        # Create notification data
        notifications = [
            {
                "user_id": uuid4(),
                "plan_id": uuid4(),
                "plan_name": "计划1",
                "exercises": [exercise],
            },
            {
                "user_id": uuid4(),
                "plan_id": uuid4(),
                "plan_name": "计划2",
                "exercises": [exercise],
            },
            {
                "user_id": uuid4(),
                "plan_id": uuid4(),
                "plan_name": "计划3",
                "exercises": [exercise],
            },
        ]

        result = await service.send_bulk_notifications(notifications)

        assert result["status"] == "completed"
        assert result["total"] == 3
        assert result["successful"] == 3
        assert result["failed"] == 0
        assert len(result["results"]) == 3
