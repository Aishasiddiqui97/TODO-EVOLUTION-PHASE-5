"""
Audit service for Event-Driven Todo Chatbot.

Maintains immutable audit trail of all task events.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import uuid

logger = logging.getLogger(__name__)


class AuditService:
    """
    Manages audit log persistence and retrieval.

    Stores all task events in an immutable log for compliance,
    debugging, and historical analysis.
    """

    def __init__(self, dapr_http_port: int = 3500):
        """
        Initialize audit service.

        Args:
            dapr_http_port: Dapr HTTP port for state API
        """
        self.dapr_http_port = dapr_http_port
        self.dapr_base_url = f"http://localhost:{dapr_http_port}"
        self.state_store_name = "statestore"

    async def log_event(
        self,
        event_type: str,
        user_id: str,
        task_id: Optional[str],
        event_data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Log an event to the audit trail.

        Args:
            event_type: Type of event (task.created, task.updated, etc.)
            user_id: User ID
            task_id: Task ID (if applicable)
            event_data: Event payload
            metadata: Optional metadata

        Returns:
            Audit log entry
        """
        try:
            import aiohttp

            # Generate audit log entry ID
            audit_id = f"audit-{uuid.uuid4()}"
            timestamp = datetime.utcnow().isoformat() + "Z"

            # Create audit log entry
            audit_entry = {
                "id": audit_id,
                "eventType": event_type,
                "userId": user_id,
                "taskId": task_id,
                "timestamp": timestamp,
                "eventData": event_data,
                "metadata": metadata or {}
            }

            # Save to state store
            url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}"

            state_data = [{
                "key": audit_id,
                "value": audit_entry
            }]

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=state_data) as response:
                    if response.status in [200, 201, 204]:
                        logger.info(f"Logged audit event: {audit_id} ({event_type})")

                        # Update user's audit index
                        await self._update_user_audit_index(user_id, audit_id, timestamp)

                        return {
                            "success": True,
                            "auditId": audit_id,
                            "timestamp": timestamp
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to save audit log: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}"
                        }

        except Exception as e:
            logger.error(f"Error logging audit event: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }

    async def _update_user_audit_index(
        self,
        user_id: str,
        audit_id: str,
        timestamp: str
    ) -> None:
        """
        Update user's audit log index.

        Maintains a list of audit log IDs per user for efficient querying.

        Args:
            user_id: User ID
            audit_id: Audit log entry ID
            timestamp: Event timestamp
        """
        try:
            import aiohttp

            index_key = f"audit-index.user.{user_id}"

            # Get existing index
            url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}/{index_key}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        index_data = await response.json()
                    else:
                        index_data = {"auditIds": []}

                # Add new audit ID (keep last 10000 entries)
                audit_ids = index_data.get("auditIds", [])
                audit_ids.append({
                    "id": audit_id,
                    "timestamp": timestamp
                })

                # Limit to last 10000 entries
                if len(audit_ids) > 10000:
                    audit_ids = audit_ids[-10000:]

                index_data["auditIds"] = audit_ids

                # Save updated index
                save_url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}"
                state_data = [{
                    "key": index_key,
                    "value": index_data
                }]

                async with session.post(save_url, json=state_data) as save_response:
                    if save_response.status not in [200, 201, 204]:
                        logger.warning(f"Failed to update audit index for user {user_id}")

        except Exception as e:
            logger.error(f"Error updating audit index: {e}", exc_info=True)

    async def get_user_audit_logs(
        self,
        user_id: str,
        limit: int = 100,
        offset: int = 0,
        event_type: Optional[str] = None,
        task_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Retrieve audit logs for a user.

        Args:
            user_id: User ID
            limit: Maximum number of entries to return
            offset: Number of entries to skip
            event_type: Filter by event type
            task_id: Filter by task ID
            start_date: Filter by start date (ISO format)
            end_date: Filter by end date (ISO format)

        Returns:
            Dictionary with audit logs and count
        """
        try:
            import aiohttp

            # Get user's audit index
            index_key = f"audit-index.user.{user_id}"
            url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}/{index_key}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return {
                            "success": True,
                            "logs": [],
                            "count": 0,
                            "total": 0
                        }

                    index_data = await response.json()
                    audit_ids = index_data.get("auditIds", [])

                # Reverse to get most recent first
                audit_ids = list(reversed(audit_ids))

                # Fetch audit log entries
                logs = []
                for audit_entry in audit_ids:
                    audit_id = audit_entry["id"]

                    # Fetch audit log
                    log_url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}/{audit_id}"

                    async with session.get(log_url) as log_response:
                        if log_response.status == 200:
                            log_data = await log_response.json()

                            # Apply filters
                            if event_type and log_data.get("eventType") != event_type:
                                continue

                            if task_id and log_data.get("taskId") != task_id:
                                continue

                            if start_date and log_data.get("timestamp", "") < start_date:
                                continue

                            if end_date and log_data.get("timestamp", "") > end_date:
                                continue

                            logs.append(log_data)

                # Apply pagination
                total = len(logs)
                logs = logs[offset:offset + limit]

                logger.info(f"Retrieved {len(logs)} audit logs for user {user_id}")

                return {
                    "success": True,
                    "logs": logs,
                    "count": len(logs),
                    "total": total
                }

        except Exception as e:
            logger.error(f"Error retrieving audit logs: {e}", exc_info=True)
            return {
                "success": False,
                "logs": [],
                "count": 0,
                "error": str(e)
            }

    async def get_task_audit_logs(
        self,
        task_id: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Retrieve all audit logs for a specific task.

        Args:
            task_id: Task ID
            user_id: User ID

        Returns:
            Dictionary with audit logs
        """
        return await self.get_user_audit_logs(
            user_id=user_id,
            task_id=task_id,
            limit=1000
        )

    async def get_audit_log_by_id(self, audit_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific audit log entry by ID.

        Args:
            audit_id: Audit log entry ID

        Returns:
            Audit log entry or None if not found
        """
        try:
            import aiohttp

            url = f"{self.dapr_base_url}/v1.0/state/{self.state_store_name}/{audit_id}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        return None

        except Exception as e:
            logger.error(f"Error retrieving audit log {audit_id}: {e}", exc_info=True)
            return None
