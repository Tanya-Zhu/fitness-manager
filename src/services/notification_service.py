"""Service for sending push notifications."""
from typing import List, Dict, Any
from uuid import UUID
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending push notifications to users."""

    async def send_push_notification(
        self,
        user_id: UUID,
        plan_id: UUID,
        plan_name: str,
        exercises: List[Any],
    ) -> Dict[str, Any]:
        """Send a push notification for a fitness plan reminder.

        Args:
            user_id: User ID to send notification to
            plan_id: Plan ID
            plan_name: Name of the fitness plan
            exercises: List of exercises in the plan

        Returns:
            Dictionary with notification status
        """
        # Format notification message
        message = self._format_message(plan_name, exercises)

        # In production, this would integrate with a push notification service
        # such as Firebase Cloud Messaging (FCM), Apple Push Notification Service (APNS),
        # or a third-party service like OneSignal or Pusher.
        #
        # For now, we'll log the notification for demonstration purposes
        logger.info(
            f"[NOTIFICATION] Sending to user {user_id} for plan {plan_id}: {message}"
        )

        # Simulate sending notification
        notification_result = {
            "status": "sent",
            "user_id": str(user_id),
            "plan_id": str(plan_id),
            "message": message,
            "timestamp": "2025-11-10T07:00:00Z",  # In production, use actual timestamp
        }

        return notification_result

    def _format_message(self, plan_name: str, exercises: List[Any]) -> str:
        """Format the notification message.

        Args:
            plan_name: Name of the fitness plan
            exercises: List of exercises

        Returns:
            Formatted notification message
        """
        # Create exercise summary
        exercise_summary = self._create_exercise_summary(exercises)

        # Format message
        message = f"🏃 健身提醒：{plan_name}\n\n"
        message += f"今天的锻炼计划：\n{exercise_summary}\n\n"
        message += "加油！坚持锻炼，保持健康！💪"

        return message

    def _create_exercise_summary(self, exercises: List[Any]) -> str:
        """Create a summary of exercises.

        Args:
            exercises: List of exercise objects

        Returns:
            Formatted exercise summary
        """
        if not exercises:
            return "暂无锻炼项目"

        summary_lines = []
        for idx, exercise in enumerate(exercises, 1):
            exercise_name = exercise.name

            # Format duration or repetitions
            if exercise.duration_minutes:
                detail = f"{exercise.duration_minutes}分钟"
            elif exercise.repetitions:
                detail = f"{exercise.repetitions}次"
            else:
                detail = ""

            # Format intensity
            intensity_map = {"low": "低强度", "medium": "中强度", "high": "高强度"}
            intensity = intensity_map.get(
                exercise.intensity.value if hasattr(exercise.intensity, "value") else exercise.intensity,
                "",
            )

            # Combine details
            exercise_line = f"{idx}. {exercise_name}"
            if detail:
                exercise_line += f" - {detail}"
            if intensity:
                exercise_line += f" ({intensity})"

            summary_lines.append(exercise_line)

        return "\n".join(summary_lines)

    async def send_bulk_notifications(
        self, notifications: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Send multiple notifications in bulk.

        This method can be used for batch sending, which is more efficient
        when multiple notifications need to be sent at once.

        Args:
            notifications: List of notification data dictionaries

        Returns:
            Dictionary with bulk send status
        """
        results = []
        for notification_data in notifications:
            result = await self.send_push_notification(
                user_id=notification_data["user_id"],
                plan_id=notification_data["plan_id"],
                plan_name=notification_data["plan_name"],
                exercises=notification_data["exercises"],
            )
            results.append(result)

        return {
            "status": "completed",
            "total": len(notifications),
            "successful": len(results),
            "failed": 0,
            "results": results,
        }
