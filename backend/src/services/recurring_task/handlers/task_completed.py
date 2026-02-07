"""
Task Completed Event Handler for Recurring Task Service.

Listens for task.completed events and creates the next instance
of recurring tasks based on their recurrence patterns.
"""

import logging
from typing import Dict, Any
from fastapi import APIRouter, Request
from pydantic import BaseModel

from ..services.recurrence_service import RecurrenceService

logger = logging.getLogger(__name__)

router = APIRouter()


class CloudEvent(BaseModel):
    """Cloud Event format from Dapr PubSub."""
    id: str
    source: str
    type: str
    specversion: str
    datacontenttype: str
    data: Dict[str, Any]


@router.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr subscription endpoint.

    Returns the list of topics this service subscribes to.
    """
    return [
        {
            "pubsubname": "task-pubsub",
            "topic": "task-events",
            "route": "/events/task-completed"
        }
    ]


@router.post("/events/task-completed")
async def handle_task_completed(request: Request):
    """
    Handle task.completed events.

    When a recurring task is completed, this handler:
    1. Checks if the task has a recurrence pattern
    2. Calculates the next occurrence date
    3. Creates a new task instance with the same properties
    4. Links the new task to the parent task

    Args:
        request: FastAPI request containing CloudEvent

    Returns:
        Success response
    """
    try:
        # Parse CloudEvent
        event_data = await request.json()
        logger.info(f"Received event: {event_data.get('type')}")

        # Extract event type and payload
        event_type = event_data.get("type", "")
        data = event_data.get("data", {})

        # Only process task.completed events
        if event_type != "task.completed":
            logger.debug(f"Ignoring event type: {event_type}")
            return {"status": "ignored", "reason": "not a task.completed event"}

        # Extract task from payload
        task = data.get("task")
        if not task:
            logger.warning("No task data in event payload")
            return {"status": "error", "reason": "missing task data"}

        # Check if task has recurrence pattern
        recurrence_pattern = task.get("recurrencePattern")
        if not recurrence_pattern:
            logger.debug(f"Task {task.get('id')} is not recurring")
            return {"status": "ignored", "reason": "task is not recurring"}

        # Create next instance using recurrence service
        recurrence_service = RecurrenceService()
        result = await recurrence_service.create_next_instance(task)

        if result["success"]:
            logger.info(
                f"Created next instance for recurring task {task.get('id')}: "
                f"new task ID {result.get('nextTaskId')}"
            )
            return {
                "status": "success",
                "nextTaskId": result.get("nextTaskId"),
                "message": result.get("message")
            }
        else:
            logger.warning(
                f"Failed to create next instance for task {task.get('id')}: "
                f"{result.get('message')}"
            )
            return {
                "status": "completed",
                "reason": result.get("message")
            }

    except Exception as e:
        logger.error(f"Error handling task.completed event: {e}", exc_info=True)
        return {
            "status": "error",
            "message": str(e)
        }
