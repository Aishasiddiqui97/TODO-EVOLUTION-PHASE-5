"""
Reconnection handler for WebSocket Sync.

Handles client reconnections and ensures they receive missed events.
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

from ..connection_manager import ConnectionManager
from .sequence_tracker import SequenceTracker
from .sync_service import SyncService

logger = logging.getLogger(__name__)


class ReconnectionHandler:
    """
    Handles WebSocket reconnections and syncs missed events.

    When a client reconnects, it can provide its last known sequence number
    to receive any events it missed while disconnected.
    """

    def __init__(
        self,
        connection_manager: ConnectionManager,
        sequence_tracker: SequenceTracker,
        sync_service: SyncService
    ):
        """
        Initialize reconnection handler.

        Args:
            connection_manager: WebSocket connection manager
            sequence_tracker: Sequence tracker
            sync_service: Sync service for fetching missed events
        """
        self.connection_manager = connection_manager
        self.sequence_tracker = sequence_tracker
        self.sync_service = sync_service

    async def handle_reconnection(
        self,
        user_id: str,
        last_sequence: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Handle a client reconnection.

        Args:
            user_id: User ID
            last_sequence: Last sequence number the client has (None for first connection)

        Returns:
            Reconnection response with sync status
        """
        current_sequence = self.sequence_tracker.get_current_sequence(user_id)

        # First-time connection
        if last_sequence is None:
            logger.info(f"First-time connection for user {user_id}")
            return {
                "status": "connected",
                "currentSequence": current_sequence,
                "missedEvents": 0,
                "syncRequired": False,
                "message": "Connected successfully"
            }

        # Check for missed events
        gap_size = self.sequence_tracker.get_gap_size(user_id, last_sequence)

        if gap_size == 0:
            logger.info(f"Reconnection for user {user_id} - no missed events")
            return {
                "status": "reconnected",
                "currentSequence": current_sequence,
                "missedEvents": 0,
                "syncRequired": False,
                "message": "Reconnected - no missed events"
            }

        # Client missed some events
        logger.info(f"Reconnection for user {user_id} - {gap_size} missed events")

        # Try to get missed events from history
        missed_events = self.sequence_tracker.get_missed_events(user_id, last_sequence)

        if len(missed_events) == gap_size:
            # We have all missed events in history
            logger.info(f"Sending {len(missed_events)} missed events to user {user_id}")
            return {
                "status": "reconnected",
                "currentSequence": current_sequence,
                "missedEvents": len(missed_events),
                "syncRequired": False,
                "events": missed_events,
                "message": f"Reconnected - sending {len(missed_events)} missed events"
            }
        else:
            # Gap is too large or events expired - need full sync
            logger.warning(f"Gap too large for user {user_id} - full sync required")
            return {
                "status": "reconnected",
                "currentSequence": current_sequence,
                "missedEvents": gap_size,
                "syncRequired": True,
                "message": "Reconnected - full sync required"
            }

    async def handle_sync_request(
        self,
        user_id: str,
        last_sequence: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Handle a client's request to sync missed events.

        Args:
            user_id: User ID
            last_sequence: Last sequence number the client has

        Returns:
            Sync response with tasks and events
        """
        try:
            # Perform full sync
            sync_result = await self.sync_service.sync_user_tasks(user_id, last_sequence)

            current_sequence = self.sequence_tracker.get_current_sequence(user_id)

            return {
                "status": "synced",
                "currentSequence": current_sequence,
                "tasks": sync_result.get("tasks", []),
                "taskCount": sync_result.get("count", 0),
                "message": f"Synced {sync_result.get('count', 0)} tasks"
            }

        except Exception as e:
            logger.error(f"Error syncing for user {user_id}: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Sync failed: {str(e)}"
            }

    async def handle_heartbeat(self, user_id: str) -> Dict[str, Any]:
        """
        Handle a heartbeat/ping from client.

        Args:
            user_id: User ID

        Returns:
            Heartbeat response
        """
        current_sequence = self.sequence_tracker.get_current_sequence(user_id)
        connection_count = self.connection_manager.get_user_connections(user_id)

        return {
            "type": "pong",
            "currentSequence": current_sequence,
            "connections": connection_count,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def handle_sequence_check(
        self,
        user_id: str,
        client_sequence: int
    ) -> Dict[str, Any]:
        """
        Check if client's sequence is up to date.

        Args:
            user_id: User ID
            client_sequence: Client's current sequence number

        Returns:
            Sequence check response
        """
        current_sequence = self.sequence_tracker.get_current_sequence(user_id)
        gap_size = self.sequence_tracker.get_gap_size(user_id, client_sequence)

        if gap_size == 0:
            return {
                "status": "up_to_date",
                "currentSequence": current_sequence,
                "clientSequence": client_sequence,
                "gap": 0
            }
        else:
            return {
                "status": "out_of_sync",
                "currentSequence": current_sequence,
                "clientSequence": client_sequence,
                "gap": gap_size,
                "syncRequired": gap_size > 100  # Arbitrary threshold
            }

    def get_reconnection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about reconnections.

        Returns:
            Dictionary with reconnection stats
        """
        return {
            "active_users": len(self.connection_manager.get_connected_users()),
            "total_connections": self.connection_manager.get_total_connections(),
            "sequence_stats": self.sequence_tracker.get_stats()
        }
