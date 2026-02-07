"""
Task updates event handler for WebSocket Sync.

Subscribes to task events and broadcasts them to connected clients.
"""

from typing import Dict, Any
import logging
from datetime import datetime

from ..services.broadcaster import Broadcaster
from ..services.sequence_tracker import SequenceTracker

logger = logging.getLogger(__name__)


class TaskUpdatesHandler:
    """
    Handles task update events from Dapr PubSub.

    Listens for task.created, task.updated, task.completed, and task.deleted
    events and broadcasts them to connected WebSocket clients.
    """

    def __init__(self, broadcaster: Broadcaster, sequence_tracker: SequenceTracker):
        """
        Initialize task updates handler.

        Args:
            broadcaster: Broadcaster service
            sequence_tracker: Sequence tracker
        """
        self.broadcaster = broadcaster
        self.sequence_tracker = sequence_tracker

    async def handle_task_created(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task.created event.

        Args:
            event_data: Event data from Dapr PubSub

        Returns:
            Response dictionary
        """
        try:
            task = event_data.get("data", {})
            user_id = task.get("userId")

            if not user_id:
                logger.warning("task.created event missing userId")
                return {"status": "error", "message": "Missing userId"}

            # Get next sequence number
            sequence = self.sequence_tracker.get_next_sequence(user_id)

            # Record event in history
            self.sequence_tracker.record_event(user_id, sequence, {
                "type": "task.created",
                "data": task
            })

            # Broadcast to connected clients
            count = await self.broadcaster.broadcast_task_created(task)

            logger.info(f"Handled task.created for task {task.get('id')} - broadcasted to {count} connection(s)")

            return {
                "status": "success",
                "sequence": sequence,
                "connections_notified": count
            }

        except Exception as e:
            logger.error(f"Error handling task.created event: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def handle_task_updated(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task.updated event.

        Args:
            event_data: Event data from Dapr PubSub

        Returns:
            Response dictionary
        """
        try:
            task = event_data.get("data", {})
            changes = event_data.get("changes", {})
            user_id = task.get("userId")

            if not user_id:
                logger.warning("task.updated event missing userId")
                return {"status": "error", "message": "Missing userId"}

            # Get next sequence number
            sequence = self.sequence_tracker.get_next_sequence(user_id)

            # Record event in history
            self.sequence_tracker.record_event(user_id, sequence, {
                "type": "task.updated",
                "data": task,
                "changes": changes
            })

            # Broadcast to connected clients
            count = await self.broadcaster.broadcast_task_updated(task, changes)

            logger.info(f"Handled task.updated for task {task.get('id')} - broadcasted to {count} connection(s)")

            return {
                "status": "success",
                "sequence": sequence,
                "connections_notified": count
            }

        except Exception as e:
            logger.error(f"Error handling task.updated event: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def handle_task_completed(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task.completed event.

        Args:
            event_data: Event data from Dapr PubSub

        Returns:
            Response dictionary
        """
        try:
            task = event_data.get("data", {})
            user_id = task.get("userId")

            if not user_id:
                logger.warning("task.completed event missing userId")
                return {"status": "error", "message": "Missing userId"}

            # Get next sequence number
            sequence = self.sequence_tracker.get_next_sequence(user_id)

            # Record event in history
            self.sequence_tracker.record_event(user_id, sequence, {
                "type": "task.completed",
                "data": task
            })

            # Broadcast to connected clients
            count = await self.broadcaster.broadcast_task_completed(task)

            logger.info(f"Handled task.completed for task {task.get('id')} - broadcasted to {count} connection(s)")

            return {
                "status": "success",
                "sequence": sequence,
                "connections_notified": count
            }

        except Exception as e:
            logger.error(f"Error handling task.completed event: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}

    async def handle_task_deleted(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task.deleted event.

        Args:
            event_data: Event data from Dapr PubSub

        Returns:
            Response dictionary
        """
        try:
            data = event_data.get("data", {})
            task_id = data.get("taskId")
            user_id = data.get("userId")

            if not user_id or not task_id:
                logger.warning("task.deleted event missing userId or taskId")
                return {"status": "error", "message": "Missing userId or taskId"}

            # Get next sequence number
            sequence = self.sequence_tracker.get_next_sequence(user_id)

            # Record event in history
            self.sequence_tracker.record_event(user_id, sequence, {
                "type": "task.deleted",
                "data": {"taskId": task_id, "userId": user_id}
            })

            # Broadcast to connected clients
            count = await self.broadcaster.broadcast_task_deleted(task_id, user_id)

            logger.info(f"Handled task.deleted for task {task_id} - broadcasted to {count} connection(s)")

            return {
                "status": "success",
                "sequence": sequence,
                "connections_notified": count
            }

        except Exception as e:
            logger.error(f"Error handling task.deleted event: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
