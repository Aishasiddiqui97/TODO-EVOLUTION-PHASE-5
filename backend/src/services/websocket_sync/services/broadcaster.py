"""
Broadcaster service for WebSocket Sync.

Handles broadcasting task updates to connected clients.
"""

from typing import Dict, Any, Optional, List
import logging
from datetime import datetime

from ..connection_manager import ConnectionManager

logger = logging.getLogger(__name__)


class Broadcaster:
    """
    Broadcasts task updates to connected WebSocket clients.

    Handles different event types and ensures messages are properly
    formatted and delivered to the correct users.
    """

    def __init__(self, connection_manager: ConnectionManager):
        """
        Initialize broadcaster.

        Args:
            connection_manager: WebSocket connection manager
        """
        self.connection_manager = connection_manager

    async def broadcast_task_created(self, task: Dict[str, Any]) -> int:
        """
        Broadcast task creation event to user's connections.

        Args:
            task: Task data

        Returns:
            Number of connections notified
        """
        user_id = task.get("userId")
        if not user_id:
            logger.warning("Task missing userId, cannot broadcast")
            return 0

        message = {
            "type": "task.created",
            "event": "task.created",
            "data": task,
            "taskId": task.get("id")
        }

        count = await self.connection_manager.broadcast_to_user(message, user_id)
        logger.info(f"Broadcasted task.created for task {task.get('id')} to {count} connection(s)")
        return count

    async def broadcast_task_updated(self, task: Dict[str, Any], changes: Optional[Dict[str, Any]] = None) -> int:
        """
        Broadcast task update event to user's connections.

        Args:
            task: Updated task data
            changes: Optional dict of changed fields

        Returns:
            Number of connections notified
        """
        user_id = task.get("userId")
        if not user_id:
            logger.warning("Task missing userId, cannot broadcast")
            return 0

        message = {
            "type": "task.updated",
            "event": "task.updated",
            "data": task,
            "taskId": task.get("id"),
            "changes": changes or {}
        }

        count = await self.connection_manager.broadcast_to_user(message, user_id)
        logger.info(f"Broadcasted task.updated for task {task.get('id')} to {count} connection(s)")
        return count

    async def broadcast_task_completed(self, task: Dict[str, Any]) -> int:
        """
        Broadcast task completion event to user's connections.

        Args:
            task: Completed task data

        Returns:
            Number of connections notified
        """
        user_id = task.get("userId")
        if not user_id:
            logger.warning("Task missing userId, cannot broadcast")
            return 0

        message = {
            "type": "task.completed",
            "event": "task.completed",
            "data": task,
            "taskId": task.get("id")
        }

        count = await self.connection_manager.broadcast_to_user(message, user_id)
        logger.info(f"Broadcasted task.completed for task {task.get('id')} to {count} connection(s)")
        return count

    async def broadcast_task_deleted(self, task_id: str, user_id: str) -> int:
        """
        Broadcast task deletion event to user's connections.

        Args:
            task_id: ID of deleted task
            user_id: User ID

        Returns:
            Number of connections notified
        """
        message = {
            "type": "task.deleted",
            "event": "task.deleted",
            "taskId": task_id,
            "data": {"id": task_id, "userId": user_id}
        }

        count = await self.connection_manager.broadcast_to_user(message, user_id)
        logger.info(f"Broadcasted task.deleted for task {task_id} to {count} connection(s)")
        return count

    async def broadcast_sync_complete(self, user_id: str, task_count: int) -> int:
        """
        Broadcast sync completion notification.

        Args:
            user_id: User ID
            task_count: Number of tasks synced

        Returns:
            Number of connections notified
        """
        message = {
            "type": "sync.complete",
            "event": "sync.complete",
            "data": {
                "taskCount": task_count,
                "timestamp": datetime.utcnow().isoformat()
            }
        }

        count = await self.connection_manager.broadcast_to_user(message, user_id)
        logger.info(f"Broadcasted sync.complete to {count} connection(s) for user {user_id}")
        return count

    async def broadcast_error(self, user_id: str, error_message: str, error_code: Optional[str] = None) -> int:
        """
        Broadcast error notification to user's connections.

        Args:
            user_id: User ID
            error_message: Error message
            error_code: Optional error code

        Returns:
            Number of connections notified
        """
        message = {
            "type": "error",
            "event": "error",
            "data": {
                "message": error_message,
                "code": error_code,
                "timestamp": datetime.utcnow().isoformat()
            }
        }

        count = await self.connection_manager.broadcast_to_user(message, user_id)
        logger.info(f"Broadcasted error to {count} connection(s) for user {user_id}")
        return count

    async def broadcast_batch_updates(self, user_id: str, events: List[Dict[str, Any]]) -> int:
        """
        Broadcast multiple events in a single message.

        Args:
            user_id: User ID
            events: List of event dictionaries

        Returns:
            Number of connections notified
        """
        message = {
            "type": "batch.updates",
            "event": "batch.updates",
            "data": {
                "events": events,
                "count": len(events)
            }
        }

        count = await self.connection_manager.broadcast_to_user(message, user_id)
        logger.info(f"Broadcasted {len(events)} batch updates to {count} connection(s) for user {user_id}")
        return count

    async def send_welcome_message(self, user_id: str, current_sequence: int) -> int:
        """
        Send welcome message to newly connected client.

        Args:
            user_id: User ID
            current_sequence: Current sequence number for the user

        Returns:
            Number of connections notified
        """
        message = {
            "type": "connection.established",
            "event": "connection.established",
            "data": {
                "userId": user_id,
                "currentSequence": current_sequence,
                "timestamp": datetime.utcnow().isoformat(),
                "message": "WebSocket connection established"
            }
        }

        count = await self.connection_manager.broadcast_to_user(message, user_id)
        logger.info(f"Sent welcome message to {count} connection(s) for user {user_id}")
        return count
