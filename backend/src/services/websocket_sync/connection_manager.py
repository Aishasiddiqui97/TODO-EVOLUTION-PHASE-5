"""
WebSocket Connection Manager for Event-Driven Todo Chatbot.

Manages WebSocket connections for real-time task synchronization across clients.
"""

from typing import Dict, Set, Optional
from fastapi import WebSocket
import logging
import asyncio
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time sync.

    Tracks active connections per user and provides methods to broadcast
    messages to specific users or all connected clients.
    """

    def __init__(self):
        """Initialize connection manager."""
        # Map of userId -> Set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

        # Map of WebSocket -> userId for reverse lookup
        self.connection_to_user: Dict[WebSocket, str] = {}

        # Map of userId -> last sequence number
        self.user_sequences: Dict[str, int] = {}

        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: str) -> None:
        """
        Register a new WebSocket connection for a user.

        Args:
            websocket: WebSocket connection
            user_id: User ID
        """
        await websocket.accept()

        async with self._lock:
            # Add to user's connection set
            if user_id not in self.active_connections:
                self.active_connections[user_id] = set()

            self.active_connections[user_id].add(websocket)
            self.connection_to_user[websocket] = user_id

            # Initialize sequence number if needed
            if user_id not in self.user_sequences:
                self.user_sequences[user_id] = 0

        logger.info(f"WebSocket connected for user {user_id}. Total connections: {len(self.active_connections[user_id])}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Unregister a WebSocket connection.

        Args:
            websocket: WebSocket connection to remove
        """
        async with self._lock:
            # Get user ID from reverse lookup
            user_id = self.connection_to_user.get(websocket)

            if user_id:
                # Remove from user's connection set
                if user_id in self.active_connections:
                    self.active_connections[user_id].discard(websocket)

                    # Clean up empty sets
                    if not self.active_connections[user_id]:
                        del self.active_connections[user_id]
                        logger.info(f"All connections closed for user {user_id}")
                    else:
                        logger.info(f"WebSocket disconnected for user {user_id}. Remaining connections: {len(self.active_connections[user_id])}")

                # Remove from reverse lookup
                del self.connection_to_user[websocket]

    async def send_personal_message(self, message: dict, websocket: WebSocket) -> None:
        """
        Send a message to a specific WebSocket connection.

        Args:
            message: Message to send (will be JSON serialized)
            websocket: Target WebSocket connection
        """
        try:
            await websocket.send_json(message)
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")
            await self.disconnect(websocket)

    async def broadcast_to_user(self, message: dict, user_id: str) -> int:
        """
        Broadcast a message to all connections for a specific user.

        Args:
            message: Message to send (will be JSON serialized)
            user_id: Target user ID

        Returns:
            Number of connections the message was sent to
        """
        connections = self.active_connections.get(user_id, set())

        if not connections:
            logger.debug(f"No active connections for user {user_id}")
            return 0

        # Add sequence number
        async with self._lock:
            self.user_sequences[user_id] = self.user_sequences.get(user_id, 0) + 1
            message["sequence"] = self.user_sequences[user_id]
            message["timestamp"] = datetime.utcnow().isoformat()

        # Send to all connections
        disconnected = []
        sent_count = 0

        for connection in connections:
            try:
                await connection.send_json(message)
                sent_count += 1
            except Exception as e:
                logger.error(f"Error broadcasting to user {user_id}: {e}")
                disconnected.append(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            await self.disconnect(connection)

        logger.info(f"Broadcasted message to {sent_count} connection(s) for user {user_id}")
        return sent_count

    async def broadcast_to_all(self, message: dict) -> int:
        """
        Broadcast a message to all connected clients.

        Args:
            message: Message to send (will be JSON serialized)

        Returns:
            Total number of connections the message was sent to
        """
        total_sent = 0

        for user_id in list(self.active_connections.keys()):
            sent = await self.broadcast_to_user(message, user_id)
            total_sent += sent

        return total_sent

    def get_user_connections(self, user_id: str) -> int:
        """
        Get the number of active connections for a user.

        Args:
            user_id: User ID

        Returns:
            Number of active connections
        """
        return len(self.active_connections.get(user_id, set()))

    def get_total_connections(self) -> int:
        """
        Get the total number of active connections across all users.

        Returns:
            Total number of connections
        """
        return sum(len(connections) for connections in self.active_connections.values())

    def get_connected_users(self) -> Set[str]:
        """
        Get the set of user IDs with active connections.

        Returns:
            Set of user IDs
        """
        return set(self.active_connections.keys())

    def get_user_sequence(self, user_id: str) -> int:
        """
        Get the current sequence number for a user.

        Args:
            user_id: User ID

        Returns:
            Current sequence number
        """
        return self.user_sequences.get(user_id, 0)

    async def send_ping(self, websocket: WebSocket) -> bool:
        """
        Send a ping message to check connection health.

        Args:
            websocket: WebSocket connection

        Returns:
            True if ping successful, False otherwise
        """
        try:
            await websocket.send_json({"type": "ping", "timestamp": datetime.utcnow().isoformat()})
            return True
        except Exception as e:
            logger.error(f"Ping failed: {e}")
            return False

    async def cleanup_stale_connections(self) -> int:
        """
        Clean up stale connections by sending pings.

        Returns:
            Number of connections cleaned up
        """
        cleaned = 0

        for user_id, connections in list(self.active_connections.items()):
            for connection in list(connections):
                if not await self.send_ping(connection):
                    await self.disconnect(connection)
                    cleaned += 1

        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} stale connection(s)")

        return cleaned
