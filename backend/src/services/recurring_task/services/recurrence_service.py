"""
Recurrence Service for Recurring Task Service.

Handles the core logic for creating next instances of recurring tasks.
"""

import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional

from ...shared.models.task import Task, RecurrencePattern
from ...shared.models.recurrence import RecurrenceType, EndConditionType
from ...shared.dapr_client.client import DaprClientWrapper
from ...shared.events.publisher import EventPublisher
from ...shared.utils.state_keys import generate_task_key
from ...shared.utils.recurrence_calculator import (
    calculate_next_occurrence,
    should_create_next_instance,
    format_next_occurrence_message,
    RecurrenceCalculatorError
)

logger = logging.getLogger(__name__)


class RecurrenceService:
    """
    Service for managing recurring task instances.

    Handles creation of next task instances based on recurrence patterns.
    """

    def __init__(self):
        """Initialize recurrence service."""
        self.dapr_client = DaprClientWrapper()
        self.event_publisher = EventPublisher("recurring-task")

    async def create_next_instance(self, completed_task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create the next instance of a recurring task.

        Args:
            completed_task: The completed task data

        Returns:
            Dict with success status, next task ID, and message
        """
        try:
            # Validate task has recurrence pattern
            recurrence_pattern_data = completed_task.get("recurrencePattern")
            if not recurrence_pattern_data:
                return {
                    "success": False,
                    "message": "Task does not have a recurrence pattern"
                }

            # Parse recurrence pattern
            recurrence_pattern = RecurrencePattern(**recurrence_pattern_data)

            # Get occurrence count
            parent_task_id = completed_task.get("parentTaskId") or completed_task.get("id")
            occurrence_key = f"chat-api.recurrence.{parent_task_id}.count"
            occurrence_data = await self.dapr_client.get_state(occurrence_key)
            occurrence_count = occurrence_data.get("count", 1) if occurrence_data else 1

            # Check if we should create next instance
            if not should_create_next_instance(recurrence_pattern, occurrence_count):
                logger.info(
                    f"Recurrence ended for task {completed_task.get('id')}: "
                    f"max occurrences reached ({occurrence_count})"
                )
                return {
                    "success": False,
                    "message": f"Recurrence ended: max occurrences ({occurrence_count}) reached"
                }

            # Calculate next occurrence date
            current_due_date = self._parse_due_datetime(completed_task)
            if not current_due_date:
                logger.warning(f"Task {completed_task.get('id')} has no due date, using current time")
                current_due_date = datetime.utcnow()

            completion_time = datetime.utcnow()
            if completed_task.get("completedAt"):
                try:
                    completion_time = datetime.fromisoformat(
                        completed_task["completedAt"].replace("Z", "+00:00")
                    )
                except Exception:
                    pass

            next_occurrence = calculate_next_occurrence(
                current_due_date,
                recurrence_pattern,
                completion_time
            )

            if not next_occurrence:
                logger.info(f"Recurrence ended for task {completed_task.get('id')}: end date reached")
                return {
                    "success": False,
                    "message": "Recurrence ended: end date reached"
                }

            # Create next task instance
            next_task_id = await self._create_task_instance(
                completed_task,
                next_occurrence,
                parent_task_id
            )

            # Increment occurrence count
            occurrence_count += 1
            await self.dapr_client.save_state(occurrence_key, {"count": occurrence_count})

            # Format success message
            message = format_next_occurrence_message(next_occurrence, recurrence_pattern)

            logger.info(
                f"Created next instance {next_task_id} for recurring task {completed_task.get('id')}"
            )

            return {
                "success": True,
                "nextTaskId": next_task_id,
                "message": message,
                "occurrenceCount": occurrence_count
            }

        except RecurrenceCalculatorError as e:
            logger.error(f"Error calculating next occurrence: {e}")
            return {
                "success": False,
                "message": f"Failed to calculate next occurrence: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Error creating next instance: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to create next instance: {str(e)}"
            }

    async def _create_task_instance(
        self,
        template_task: Dict[str, Any],
        next_due_date: datetime,
        parent_task_id: str
    ) -> str:
        """
        Create a new task instance based on template task.

        Args:
            template_task: The completed task to use as template
            next_due_date: Due date for the next instance
            parent_task_id: ID of the parent recurring task

        Returns:
            ID of the newly created task
        """
        # Generate new task ID
        new_task_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat() + "Z"

        # Extract due date and time from next occurrence
        next_due_date_str = next_due_date.strftime("%Y-%m-%d")
        next_due_time_str = next_due_date.strftime("%H:%M")

        # Create new task data based on template
        new_task_data = {
            "id": new_task_id,
            "userId": template_task.get("userId"),
            "title": template_task.get("title"),
            "description": template_task.get("description"),
            "priority": template_task.get("priority", "medium"),
            "dueDate": next_due_date_str,
            "dueTime": next_due_time_str,
            "tags": template_task.get("tags", []),
            "status": "pending",
            "recurrencePattern": template_task.get("recurrencePattern"),
            "parentTaskId": parent_task_id,
            "createdAt": now,
            "updatedAt": now,
            "completedAt": None
        }

        # Validate with Pydantic model
        new_task = Task(**new_task_data)

        # Save to state store
        state_key = generate_task_key(template_task.get("userId"), new_task_id)
        await self.dapr_client.save_state(state_key, new_task.dict())

        # Update task index for user
        index_key = f"chat-api.task-index.user.{template_task.get('userId')}"
        task_index = await self.dapr_client.get_state(index_key) or {"taskIds": []}
        if new_task_id not in task_index["taskIds"]:
            task_index["taskIds"].append(new_task_id)
            await self.dapr_client.save_state(index_key, task_index)

        # Publish task.created event
        await self.event_publisher.publish(
            topic="task-events",
            event_type="task.created",
            user_id=template_task.get("userId"),
            payload={
                "task": new_task.dict(),
                "isRecurringInstance": True,
                "parentTaskId": parent_task_id
            }
        )

        return new_task_id

    def _parse_due_datetime(self, task: Dict[str, Any]) -> Optional[datetime]:
        """
        Parse due date and time from task data.

        Args:
            task: Task data

        Returns:
            datetime object or None if no due date
        """
        due_date_str = task.get("dueDate")
        if not due_date_str:
            return None

        due_time_str = task.get("dueTime", "09:00")

        try:
            # Combine date and time
            datetime_str = f"{due_date_str}T{due_time_str}:00"
            return datetime.fromisoformat(datetime_str)
        except Exception as e:
            logger.warning(f"Failed to parse due datetime: {e}")
            return None
