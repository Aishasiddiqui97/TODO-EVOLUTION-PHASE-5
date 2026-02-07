"""
Sync service for WebSocket Sync.

Handles syncing missed events and tasks for reconnected clients.
"""

from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class SyncService:
    """
    Syncs tasks and events for clients that missed updates.

    When a client reconnects after being offline, this service fetches
    the current state of all tasks to ensure the client is up to date.
    """

    def __init__(self, dapr_http_port: int = 3500):
        """
        Initialize sync service.

        Args:
            dapr_http_port: Dapr HTTP port for API calls
        """
        self.dapr_http_port = dapr_http_port
        self.dapr_base_url = f"http://localhost:{dapr_http_port}"

    async def sync_user_tasks(
        self,
        user_id: str,
        last_sequence: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Sync all tasks for a user.

        Fetches the current state of all tasks from the Chat API service.

        Args:
            user_id: User ID
            last_sequence: Last sequence number the client has (for logging)

        Returns:
            Dictionary with tasks and count
        """
        try:
            import aiohttp

            # Call Chat API to get all tasks for user
            url = f"{self.dapr_base_url}/v1.0/invoke/chat-api/method/api/v1/tasks"
            params = {"userId": user_id, "limit": 1000}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        tasks = data.get("tasks", [])

                        logger.info(f"Synced {len(tasks)} tasks for user {user_id}")

                        return {
                            "success": True,
                            "tasks": tasks,
                            "count": len(tasks),
                            "lastSequence": last_sequence
                        }
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to sync tasks: {response.status} - {error_text}")
                        return {
                            "success": False,
                            "tasks": [],
                            "count": 0,
                            "error": f"HTTP {response.status}"
                        }

        except Exception as e:
            logger.error(f"Error syncing tasks for user {user_id}: {e}", exc_info=True)
            return {
                "success": False,
                "tasks": [],
                "count": 0,
                "error": str(e)
            }

    async def sync_specific_tasks(
        self,
        user_id: str,
        task_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Sync specific tasks by ID.

        Args:
            user_id: User ID
            task_ids: List of task IDs to sync

        Returns:
            Dictionary with tasks and count
        """
        try:
            import aiohttp

            tasks = []

            async with aiohttp.ClientSession() as session:
                for task_id in task_ids:
                    url = f"{self.dapr_base_url}/v1.0/invoke/chat-api/method/api/v1/tasks/{task_id}"

                    try:
                        async with session.get(url) as response:
                            if response.status == 200:
                                task_data = await response.json()
                                tasks.append(task_data)
                            else:
                                logger.warning(f"Failed to fetch task {task_id}: {response.status}")
                    except Exception as e:
                        logger.error(f"Error fetching task {task_id}: {e}")
                        continue

            logger.info(f"Synced {len(tasks)} specific tasks for user {user_id}")

            return {
                "success": True,
                "tasks": tasks,
                "count": len(tasks)
            }

        except Exception as e:
            logger.error(f"Error syncing specific tasks: {e}", exc_info=True)
            return {
                "success": False,
                "tasks": [],
                "count": 0,
                "error": str(e)
            }

    async def get_task_by_id(self, task_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a single task by ID.

        Args:
            task_id: Task ID

        Returns:
            Task data or None if not found
        """
        try:
            import aiohttp

            url = f"{self.dapr_base_url}/v1.0/invoke/chat-api/method/api/v1/tasks/{task_id}"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.warning(f"Task {task_id} not found: {response.status}")
                        return None

        except Exception as e:
            logger.error(f"Error fetching task {task_id}: {e}", exc_info=True)
            return None

    async def verify_sync_integrity(
        self,
        user_id: str,
        client_task_ids: List[str]
    ) -> Dict[str, Any]:
        """
        Verify sync integrity by comparing client's task list with server.

        Args:
            user_id: User ID
            client_task_ids: List of task IDs the client has

        Returns:
            Dictionary with missing and extra task IDs
        """
        try:
            # Get all server tasks
            sync_result = await self.sync_user_tasks(user_id)

            if not sync_result.get("success"):
                return {
                    "success": False,
                    "error": "Failed to fetch server tasks"
                }

            server_tasks = sync_result.get("tasks", [])
            server_task_ids = {task["id"] for task in server_tasks}
            client_task_ids_set = set(client_task_ids)

            # Find differences
            missing_on_client = server_task_ids - client_task_ids_set
            extra_on_client = client_task_ids_set - server_task_ids

            logger.info(
                f"Sync integrity check for user {user_id}: "
                f"{len(missing_on_client)} missing, {len(extra_on_client)} extra"
            )

            return {
                "success": True,
                "missingOnClient": list(missing_on_client),
                "extraOnClient": list(extra_on_client),
                "inSync": len(missing_on_client) == 0 and len(extra_on_client) == 0
            }

        except Exception as e:
            logger.error(f"Error verifying sync integrity: {e}", exc_info=True)
            return {
                "success": False,
                "error": str(e)
            }
