"""
Task service for managing task operations and event publishing.

Handles task CRUD operations with Dapr state store and publishes events.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

from shared.dapr_client.client import DaprClient
from shared.events.publisher import EventPublisher
from shared.events.schemas import TaskEvent, EventType
from shared.models.task import Task
from shared.utils.state_keys import generate_task_key, generate_user_tasks_key
from shared.utils.idempotency import IdempotencyChecker

logger = logging.getLogger(__name__)


class TaskService:
    """Service for task operations with state management and event publishing."""

    def __init__(self, dapr_client: DaprClient, event_publisher: EventPublisher):
        """
        Initialize task service.

        Args:
            dapr_client: Dapr client for state operations
            event_publisher: Event publisher for task events
        """
        self.dapr_client = dapr_client
        self.event_publisher = event_publisher
        self.idempotency = IdempotencyChecker(dapr_client)

    async def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: str = "medium",
        due_date: Optional[str] = None,
        due_time: Optional[str] = None,
        tags: Optional[List[str]] = None,
        recurrence_pattern: Optional[str] = None,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a new task.

        Args:
            user_id: User ID
            title: Task title
            description: Task description
            priority: Task priority (low, medium, high)
            due_date: Due date (ISO format)
            due_time: Due time (HH:MM format)
            tags: List of tags
            recurrence_pattern: Recurrence pattern
            idempotency_key: Optional idempotency key

        Returns:
            Created task data
        """
        try:
            # Check idempotency
            if idempotency_key:
                cached = await self.idempotency.check(idempotency_key)
                if cached:
                    logger.info(f"Returning cached result for idempotency key: {idempotency_key}")
                    return cached

            # Generate task ID
            task_id = f"task-{uuid.uuid4()}"
            timestamp = datetime.utcnow().isoformat() + "Z"

            # Create task object
            task_data = {
                "id": task_id,
                "userId": user_id,
                "title": title,
                "description": description or "",
                "priority": priority,
                "status": "pending",
                "dueDate": due_date,
                "dueTime": due_time,
                "tags": tags or [],
                "recurrencePattern": recurrence_pattern,
                "createdAt": timestamp,
                "updatedAt": timestamp,
                "completedAt": None
            }

            # Save to state store
            task_key = generate_task_key(task_id)
            await self.dapr_client.save_state(task_key, task_data)

            # Update user's task list
            await self._add_task_to_user_list(user_id, task_id)

            # Publish event
            await self.event_publisher.publish_task_event(
                event_type=EventType.TASK_CREATED,
                task_id=task_id,
                user_id=user_id,
                payload={"task": task_data}
            )

            # Cache result for idempotency
            if idempotency_key:
                await self.idempotency.store(idempotency_key, task_data)

            logger.info(f"Task created: {task_id} for user: {user_id}")
            return task_data

        except Exception as e:
            logger.error(f"Error creating task: {e}", exc_info=True)
            raise

    async def get_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task data or None if not found
        """
        try:
            task_key = generate_task_key(task_id)
            task_data = await self.dapr_client.get_state(task_key)
            return task_data
        except Exception as e:
            logger.error(f"Error getting task {task_id}: {e}", exc_info=True)
            return None

    async def list_tasks(
        self,
        user_id: str,
        status: Optional[str] = None,
        priority: Optional[str] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        List tasks for a user with optional filters.

        Args:
            user_id: User ID
            status: Filter by status
            priority: Filter by priority
            tags: Filter by tags

        Returns:
            List of tasks
        """
        try:
            # Get user's task list
            user_tasks_key = generate_user_tasks_key(user_id)
            task_ids = await self.dapr_client.get_state(user_tasks_key) or []

            # Fetch all tasks
            tasks = []
            for task_id in task_ids:
                task = await self.get_task(task_id)
                if task:
                    # Apply filters
                    if status and task.get("status") != status:
                        continue
                    if priority and task.get("priority") != priority:
                        continue
                    if tags:
                        task_tags = task.get("tags", [])
                        if not any(tag in task_tags for tag in tags):
                            continue
                    tasks.append(task)

            return tasks

        except Exception as e:
            logger.error(f"Error listing tasks for user {user_id}: {e}", exc_info=True)
            return []

    async def update_task(
        self,
        task_id: str,
        updates: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update a task.

        Args:
            task_id: Task ID
            updates: Dictionary of fields to update

        Returns:
            Updated task data or None if not found
        """
        try:
            # Get existing task
            task = await self.get_task(task_id)
            if not task:
                logger.warning(f"Task not found: {task_id}")
                return None

            # Update fields
            task.update(updates)
            task["updatedAt"] = datetime.utcnow().isoformat() + "Z"

            # Save to state store
            task_key = generate_task_key(task_id)
            await self.dapr_client.save_state(task_key, task)

            # Publish event
            await self.event_publisher.publish_task_event(
                event_type=EventType.TASK_UPDATED,
                task_id=task_id,
                user_id=task["userId"],
                payload={"task": task, "updates": updates}
            )

            logger.info(f"Task updated: {task_id}")
            return task

        except Exception as e:
            logger.error(f"Error updating task {task_id}: {e}", exc_info=True)
            raise

    async def complete_task(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Mark a task as completed.

        Args:
            task_id: Task ID

        Returns:
            Updated task data or None if not found
        """
        try:
            # Get existing task
            task = await self.get_task(task_id)
            if not task:
                logger.warning(f"Task not found: {task_id}")
                return None

            # Update status
            task["status"] = "completed"
            task["completedAt"] = datetime.utcnow().isoformat() + "Z"
            task["updatedAt"] = task["completedAt"]

            # Save to state store
            task_key = generate_task_key(task_id)
            await self.dapr_client.save_state(task_key, task)

            # Publish event
            await self.event_publisher.publish_task_event(
                event_type=EventType.TASK_COMPLETED,
                task_id=task_id,
                user_id=task["userId"],
                payload={"task": task}
            )

            logger.info(f"Task completed: {task_id}")
            return task

        except Exception as e:
            logger.error(f"Error completing task {task_id}: {e}", exc_info=True)
            raise

    async def delete_task(self, task_id: str) -> bool:
        """
        Delete a task.

        Args:
            task_id: Task ID

        Returns:
            True if deleted, False if not found
        """
        try:
            # Get existing task
            task = await self.get_task(task_id)
            if not task:
                logger.warning(f"Task not found: {task_id}")
                return False

            user_id = task["userId"]

            # Delete from state store
            task_key = generate_task_key(task_id)
            await self.dapr_client.delete_state(task_key)

            # Remove from user's task list
            await self._remove_task_from_user_list(user_id, task_id)

            # Publish event
            await self.event_publisher.publish_task_event(
                event_type=EventType.TASK_DELETED,
                task_id=task_id,
                user_id=user_id,
                payload={"task": task}
            )

            logger.info(f"Task deleted: {task_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting task {task_id}: {e}", exc_info=True)
            raise

    async def _add_task_to_user_list(self, user_id: str, task_id: str):
        """Add task ID to user's task list."""
        user_tasks_key = generate_user_tasks_key(user_id)
        task_ids = await self.dapr_client.get_state(user_tasks_key) or []
        if task_id not in task_ids:
            task_ids.append(task_id)
            await self.dapr_client.save_state(user_tasks_key, task_ids)

    async def _remove_task_from_user_list(self, user_id: str, task_id: str):
        """Remove task ID from user's task list."""
        user_tasks_key = generate_user_tasks_key(user_id)
        task_ids = await self.dapr_client.get_state(user_tasks_key) or []
        if task_id in task_ids:
            task_ids.remove(task_id)
            await self.dapr_client.save_state(user_tasks_key, task_ids)
