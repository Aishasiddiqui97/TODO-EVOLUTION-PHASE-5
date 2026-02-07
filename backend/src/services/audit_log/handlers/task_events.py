"""
Task events handler for Audit Log service.

Subscribes to task events and logs them to the audit trail.
"""

from typing import Dict, Any
import logging

from ..services.audit_service import AuditService

logger = logging.getLogger(__name__)


class TaskEventsHandler:
    """
    Handles task events from Dapr PubSub and logs them to audit trail.

    Processes task.created, task.updated, task.completed, and task.deleted
    events and creates immutable audit log entries.
    """

    def __init__(self, audit_service: AuditService):
        """
        Initialize task events handler.

        Args:
            audit_service: Audit service for persistence
        """
        self.audit_service = audit_service

    async def handle_task_created(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle task.created event.

        Args:
            event_data: Event data from Dapr PubSub

        Returns:
            Response dictionary
        """
        try:
            task = event_data.get("data", {}).get("task", {})
            user_id = task.get("userId")
            task_id = task.get("id")

            if not user_id or not task_id:
                logger.warning("task.created event missing userId or taskId")
                return {"status": "error", "message": "Missing userId or taskId"}

            # Log to audit trail
            result = await self.audit_service.log_event(
                event_type="task.created",
                user_id=user_id,
                task_id=task_id,
                event_data={
                    "task": task,
                    "action": "created"
                },
                metadata={
                    "source": "task-events",
                    "eventId": event_data.get("id")
                }
            )

            if result.get("success"):
                logger.info(f"Logged task.created for task {task_id} - audit ID: {result.get('auditId')}")
                return {"status": "success", "auditId": result.get("auditId")}
            else:
                logger.error(f"Failed to log task.created: {result.get('error')}")
                return {"status": "error", "message": result.get("error")}

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
            payload = event_data.get("data", {})
            task = payload.get("task", {})
            updated_fields = payload.get("updatedFields", [])

            user_id = task.get("userId")
            task_id = task.get("id")

            if not user_id or not task_id:
                logger.warning("task.updated event missing userId or taskId")
                return {"status": "error", "message": "Missing userId or taskId"}

            # Log to audit trail
            result = await self.audit_service.log_event(
                event_type="task.updated",
                user_id=user_id,
                task_id=task_id,
                event_data={
                    "task": task,
                    "updatedFields": updated_fields,
                    "action": "updated"
                },
                metadata={
                    "source": "task-events",
                    "eventId": event_data.get("id")
                }
            )

            if result.get("success"):
                logger.info(f"Logged task.updated for task {task_id} - audit ID: {result.get('auditId')}")
                return {"status": "success", "auditId": result.get("auditId")}
            else:
                logger.error(f"Failed to log task.updated: {result.get('error')}")
                return {"status": "error", "message": result.get("error")}

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
            task = event_data.get("data", {}).get("task", {})
            user_id = task.get("userId")
            task_id = task.get("id")

            if not user_id or not task_id:
                logger.warning("task.completed event missing userId or taskId")
                return {"status": "error", "message": "Missing userId or taskId"}

            # Log to audit trail
            result = await self.audit_service.log_event(
                event_type="task.completed",
                user_id=user_id,
                task_id=task_id,
                event_data={
                    "task": task,
                    "action": "completed",
                    "completedAt": task.get("completedAt")
                },
                metadata={
                    "source": "task-events",
                    "eventId": event_data.get("id")
                }
            )

            if result.get("success"):
                logger.info(f"Logged task.completed for task {task_id} - audit ID: {result.get('auditId')}")
                return {"status": "success", "auditId": result.get("auditId")}
            else:
                logger.error(f"Failed to log task.completed: {result.get('error')}")
                return {"status": "error", "message": result.get("error")}

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
            payload = event_data.get("data", {})
            task_id = payload.get("taskId")
            task = payload.get("task", {})
            user_id = task.get("userId") or payload.get("userId")

            if not user_id or not task_id:
                logger.warning("task.deleted event missing userId or taskId")
                return {"status": "error", "message": "Missing userId or taskId"}

            # Log to audit trail
            result = await self.audit_service.log_event(
                event_type="task.deleted",
                user_id=user_id,
                task_id=task_id,
                event_data={
                    "taskId": task_id,
                    "task": task,
                    "action": "deleted"
                },
                metadata={
                    "source": "task-events",
                    "eventId": event_data.get("id")
                }
            )

            if result.get("success"):
                logger.info(f"Logged task.deleted for task {task_id} - audit ID: {result.get('auditId')}")
                return {"status": "success", "auditId": result.get("auditId")}
            else:
                logger.error(f"Failed to log task.deleted: {result.get('error')}")
                return {"status": "error", "message": result.get("error")}

        except Exception as e:
            logger.error(f"Error handling task.deleted event: {e}", exc_info=True)
            return {"status": "error", "message": str(e)}
