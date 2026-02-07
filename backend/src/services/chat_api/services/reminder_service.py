"""
Reminder scheduling service for Chat API.

Handles scheduling of task reminders based on due dates and user preferences.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

from src.shared.dapr_client.client import DaprClientWrapper
from src.shared.events.publisher import EventPublisher
from src.shared.models.preferences import UserPreferences

logger = logging.getLogger(__name__)


class ReminderService:
    """
    Service for scheduling task reminders.

    Integrates with Dapr Jobs API to schedule reminder notifications
    at user-configured advance times before task due dates.
    """

    def __init__(self):
        """Initialize reminder service."""
        self.dapr_client = DaprClientWrapper()
        self.event_publisher = EventPublisher("chat-api")

    async def schedule_reminder(
        self,
        task_id: str,
        user_id: str,
        due_datetime: datetime,
        task_title: str
    ) -> Dict[str, Any]:
        """
        Schedule a reminder for a task.

        Creates two reminders:
        1. Advance reminder (based on user preferences, default 24 hours before)
        2. Due time reminder (when task is actually due)

        Args:
            task_id: ID of the task
            user_id: ID of the user
            due_datetime: When the task is due
            task_title: Title of the task

        Returns:
            Dict with success status and scheduled reminder details
        """
        try:
            # Get user preferences for reminder advance time
            preferences = await self._get_user_preferences(user_id)
            advance_hours = preferences.reminderAdvanceTime if preferences else 24

            # Calculate reminder times
            now = datetime.utcnow()
            advance_reminder_time = due_datetime - timedelta(hours=advance_hours)
            due_reminder_time = due_datetime

            scheduled_reminders = []

            # Schedule advance reminder if it's in the future
            if advance_reminder_time > now:
                advance_result = await self._publish_reminder_event(
                    task_id=task_id,
                    user_id=user_id,
                    reminder_time=advance_reminder_time,
                    reminder_type="advance",
                    task_title=task_title,
                    advance_hours=advance_hours
                )
                scheduled_reminders.append({
                    "type": "advance",
                    "time": advance_reminder_time.isoformat(),
                    "scheduled": advance_result
                })
                logger.info(
                    f"Scheduled advance reminder for task {task_id} at "
                    f"{advance_reminder_time.isoformat()}"
                )

            # Schedule due time reminder if it's in the future
            if due_reminder_time > now:
                due_result = await self._publish_reminder_event(
                    task_id=task_id,
                    user_id=user_id,
                    reminder_time=due_reminder_time,
                    reminder_type="due",
                    task_title=task_title
                )
                scheduled_reminders.append({
                    "type": "due",
                    "time": due_reminder_time.isoformat(),
                    "scheduled": due_result
                })
                logger.info(
                    f"Scheduled due reminder for task {task_id} at "
                    f"{due_reminder_time.isoformat()}"
                )

            return {
                "success": True,
                "reminders": scheduled_reminders,
                "message": f"Scheduled {len(scheduled_reminders)} reminder(s)"
            }

        except Exception as e:
            logger.error(f"Error scheduling reminder: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to schedule reminder: {str(e)}"
            }

    async def cancel_reminders(
        self,
        task_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Cancel all reminders for a task.

        Args:
            task_id: ID of the task
            user_id: ID of the user

        Returns:
            Dict with success status
        """
        try:
            # Publish reminder.cancelled event
            await self.event_publisher.publish(
                topic="reminder-events",
                event_type="reminder.cancelled",
                user_id=user_id,
                payload={
                    "taskId": task_id,
                    "userId": user_id,
                    "cancelledAt": datetime.utcnow().isoformat()
                }
            )

            logger.info(f"Cancelled reminders for task {task_id}")

            return {
                "success": True,
                "message": "Reminders cancelled successfully"
            }

        except Exception as e:
            logger.error(f"Error cancelling reminders: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to cancel reminders: {str(e)}"
            }

    async def reschedule_reminders(
        self,
        task_id: str,
        user_id: str,
        new_due_datetime: datetime,
        task_title: str
    ) -> Dict[str, Any]:
        """
        Reschedule reminders for a task with a new due date.

        Args:
            task_id: ID of the task
            user_id: ID of the user
            new_due_datetime: New due date/time
            task_title: Title of the task

        Returns:
            Dict with success status
        """
        try:
            # Cancel existing reminders
            await self.cancel_reminders(task_id, user_id)

            # Schedule new reminders
            result = await self.schedule_reminder(
                task_id=task_id,
                user_id=user_id,
                due_datetime=new_due_datetime,
                task_title=task_title
            )

            logger.info(f"Rescheduled reminders for task {task_id}")

            return result

        except Exception as e:
            logger.error(f"Error rescheduling reminders: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to reschedule reminders: {str(e)}"
            }

    async def _publish_reminder_event(
        self,
        task_id: str,
        user_id: str,
        reminder_time: datetime,
        reminder_type: str,
        task_title: str,
        advance_hours: Optional[int] = None
    ) -> bool:
        """
        Publish a reminder.scheduled event.

        Args:
            task_id: ID of the task
            user_id: ID of the user
            reminder_time: When to send the reminder
            reminder_type: Type of reminder (advance/due)
            task_title: Title of the task
            advance_hours: Hours before due time (for advance reminders)

        Returns:
            True if event published successfully
        """
        try:
            payload = {
                "taskId": task_id,
                "userId": user_id,
                "reminderTime": reminder_time.isoformat(),
                "reminderType": reminder_type,
                "taskTitle": task_title,
                "scheduledAt": datetime.utcnow().isoformat()
            }

            if advance_hours:
                payload["advanceHours"] = advance_hours

            await self.event_publisher.publish(
                topic="reminder-events",
                event_type="reminder.scheduled",
                user_id=user_id,
                payload=payload
            )

            return True

        except Exception as e:
            logger.error(f"Error publishing reminder event: {e}", exc_info=True)
            return False

    async def _get_user_preferences(self, user_id: str) -> Optional[UserPreferences]:
        """
        Get user preferences for reminder settings.

        Args:
            user_id: ID of the user

        Returns:
            UserPreferences object or None
        """
        try:
            state_key = f"chat-api.preferences.user.{user_id}"
            preferences_data = await self.dapr_client.get_state(state_key)

            if preferences_data:
                return UserPreferences(**preferences_data)

            return None

        except Exception as e:
            logger.warning(f"Error getting user preferences: {e}")
            return None

    def parse_due_datetime(self, due_date: str, due_time: str) -> Optional[datetime]:
        """
        Parse due date and time into datetime object.

        Args:
            due_date: Date string (YYYY-MM-DD)
            due_time: Time string (HH:MM)

        Returns:
            datetime object or None if parsing fails
        """
        try:
            if not due_date:
                return None

            time_str = due_time if due_time else "09:00"
            datetime_str = f"{due_date}T{time_str}:00"

            return datetime.fromisoformat(datetime_str)

        except Exception as e:
            logger.warning(f"Error parsing due datetime: {e}")
            return None
