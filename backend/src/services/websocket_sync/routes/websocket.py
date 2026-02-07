"""
WebSocket endpoint for real-time sync.

Provides WebSocket connection for clients to receive real-time task updates.
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from typing import Optional
import logging
import json

from ..connection_manager import ConnectionManager
from ..services.reconnection_handler import ReconnectionHandler
from ..services.broadcaster import Broadcaster

logger = logging.getLogger(__name__)

router = APIRouter()


# These will be injected by the main app
connection_manager: Optional[ConnectionManager] = None
reconnection_handler: Optional[ReconnectionHandler] = None
broadcaster: Optional[Broadcaster] = None


def init_websocket_router(
    conn_mgr: ConnectionManager,
    reconn_handler: ReconnectionHandler,
    bcast: Broadcaster
):
    """
    Initialize the WebSocket router with dependencies.

    Args:
        conn_mgr: Connection manager
        reconn_handler: Reconnection handler
        bcast: Broadcaster
    """
    global connection_manager, reconnection_handler, broadcaster
    connection_manager = conn_mgr
    reconnection_handler = reconn_handler
    broadcaster = bcast


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    userId: str = Query(..., description="User ID for authentication"),
    lastSequence: Optional[int] = Query(None, description="Last sequence number client has")
):
    """
    WebSocket endpoint for real-time task synchronization.

    Clients connect with their userId and optionally their last known sequence number.
    The server will send any missed events and then stream real-time updates.

    Args:
        websocket: WebSocket connection
        userId: User ID
        lastSequence: Last sequence number the client has (for reconnection)
    """
    if not connection_manager or not reconnection_handler or not broadcaster:
        logger.error("WebSocket dependencies not initialized")
        await websocket.close(code=1011, reason="Server not ready")
        return

    try:
        # Accept connection
        await connection_manager.connect(websocket, userId)
        logger.info(f"WebSocket connected: userId={userId}, lastSequence={lastSequence}")

        # Handle reconnection and send initial sync data
        reconnection_response = await reconnection_handler.handle_reconnection(userId, lastSequence)

        # Send reconnection response
        await websocket.send_json({
            "type": "connection.established",
            "data": reconnection_response
        })

        # If there are missed events, send them
        if reconnection_response.get("events"):
            await websocket.send_json({
                "type": "sync.events",
                "data": {
                    "events": reconnection_response["events"],
                    "count": len(reconnection_response["events"])
                }
            })

        # If full sync is required, trigger it
        if reconnection_response.get("syncRequired"):
            sync_response = await reconnection_handler.handle_sync_request(userId, lastSequence)
            await websocket.send_json({
                "type": "sync.full",
                "data": sync_response
            })

        # Listen for client messages
        while True:
            try:
                # Receive message from client
                data = await websocket.receive_text()
                message = json.loads(data)

                # Handle different message types
                message_type = message.get("type")

                if message_type == "ping":
                    # Heartbeat
                    response = await reconnection_handler.handle_heartbeat(userId)
                    await websocket.send_json(response)

                elif message_type == "sync.request":
                    # Client requesting full sync
                    last_seq = message.get("lastSequence")
                    sync_response = await reconnection_handler.handle_sync_request(userId, last_seq)
                    await websocket.send_json({
                        "type": "sync.full",
                        "data": sync_response
                    })

                elif message_type == "sequence.check":
                    # Client checking if sequence is up to date
                    client_seq = message.get("sequence", 0)
                    check_response = await reconnection_handler.handle_sequence_check(userId, client_seq)
                    await websocket.send_json({
                        "type": "sequence.status",
                        "data": check_response
                    })

                else:
                    logger.warning(f"Unknown message type: {message_type}")
                    await websocket.send_json({
                        "type": "error",
                        "data": {
                            "message": f"Unknown message type: {message_type}"
                        }
                    })

            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON from client: {e}")
                await websocket.send_json({
                    "type": "error",
                    "data": {"message": "Invalid JSON"}
                })

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: userId={userId}")
        await connection_manager.disconnect(websocket)

    except Exception as e:
        logger.error(f"WebSocket error for userId={userId}: {e}", exc_info=True)
        try:
            await connection_manager.disconnect(websocket)
        except:
            pass


@router.get("/connections/stats")
async def get_connection_stats():
    """
    Get statistics about active WebSocket connections.

    Returns:
        Connection statistics
    """
    if not connection_manager or not reconnection_handler:
        return {"error": "Service not ready"}

    return reconnection_handler.get_reconnection_stats()


@router.post("/broadcast/test")
async def test_broadcast(user_id: str, message: str):
    """
    Test endpoint to broadcast a message to a user's connections.

    Args:
        user_id: User ID
        message: Test message

    Returns:
        Broadcast result
    """
    if not connection_manager:
        return {"error": "Service not ready"}

    count = await connection_manager.broadcast_to_user(
        {"type": "test", "message": message},
        user_id
    )

    return {
        "success": True,
        "connections_notified": count
    }
