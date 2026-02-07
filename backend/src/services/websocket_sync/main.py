"""
WebSocket Sync Service for Event-Driven Todo Chatbot.

Provides real-time task synchronization across multiple clients via WebSocket.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import asyncio
from contextlib import asynccontextmanager

from .connection_manager import ConnectionManager
from .services.broadcaster import Broadcaster
from .services.sequence_tracker import SequenceTracker
from .services.reconnection_handler import ReconnectionHandler
from .services.sync_service import SyncService
from .handlers.task_updates import TaskUpdatesHandler
from .routes import websocket, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
connection_manager = ConnectionManager()
sequence_tracker = SequenceTracker(max_history_hours=24)
sync_service = SyncService(dapr_http_port=3500)
broadcaster = Broadcaster(connection_manager)
reconnection_handler = ReconnectionHandler(connection_manager, sequence_tracker, sync_service)
task_updates_handler = TaskUpdatesHandler(broadcaster, sequence_tracker)

# Background task for cleanup
cleanup_task = None


async def cleanup_background_task():
    """Background task to clean up stale connections and old events."""
    while True:
        try:
            await asyncio.sleep(300)  # Run every 5 minutes

            # Clean up stale connections
            cleaned_connections = await connection_manager.cleanup_stale_connections()
            if cleaned_connections > 0:
                logger.info(f"Cleaned up {cleaned_connections} stale connections")

            # Clean up old events
            cleaned_events = sequence_tracker.cleanup_all_old_events()
            if cleaned_events > 0:
                logger.info(f"Cleaned up {cleaned_events} old events")

        except Exception as e:
            logger.error(f"Error in cleanup task: {e}", exc_info=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown."""
    # Startup
    logger.info("Starting WebSocket Sync Service...")

    # Start background cleanup task
    global cleanup_task
    cleanup_task = asyncio.create_task(cleanup_background_task())

    logger.info("WebSocket Sync Service started successfully")

    yield

    # Shutdown
    logger.info("Shutting down WebSocket Sync Service...")

    # Cancel cleanup task
    if cleanup_task:
        cleanup_task.cancel()
        try:
            await cleanup_task
        except asyncio.CancelledError:
            pass

    logger.info("WebSocket Sync Service stopped")


# Create FastAPI app
app = FastAPI(
    title="WebSocket Sync Service",
    description="Real-time task synchronization service",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize WebSocket router with dependencies
websocket.init_websocket_router(connection_manager, reconnection_handler, broadcaster)

# Include routers
app.include_router(websocket.router, tags=["websocket"])
app.include_router(health.router, tags=["health"])


# Dapr PubSub subscription endpoint
@app.get("/dapr/subscribe")
async def subscribe():
    """
    Dapr PubSub subscription endpoint.

    Returns the list of topics this service subscribes to.
    """
    return [
        {
            "pubsubname": "task-pubsub",
            "topic": "task-events",
            "route": "/events/task-events"
        }
    ]


# Event handlers
@app.post("/events/task-events")
async def handle_task_event(event: dict):
    """
    Handle task events from Dapr PubSub.

    Routes events to appropriate handlers based on event type.

    Args:
        event: CloudEvent from Dapr PubSub

    Returns:
        Handler response
    """
    try:
        event_type = event.get("type", "")
        logger.info(f"Received event: {event_type}")

        if event_type == "task.created":
            return await task_updates_handler.handle_task_created(event)
        elif event_type == "task.updated":
            return await task_updates_handler.handle_task_updated(event)
        elif event_type == "task.completed":
            return await task_updates_handler.handle_task_completed(event)
        elif event_type == "task.deleted":
            return await task_updates_handler.handle_task_deleted(event)
        else:
            logger.warning(f"Unknown event type: {event_type}")
            return {"status": "ignored", "message": f"Unknown event type: {event_type}"}

    except Exception as e:
        logger.error(f"Error handling task event: {e}", exc_info=True)
        return {"status": "error", "message": str(e)}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "websocket-sync",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/stats")
async def get_stats():
    """
    Get service statistics.

    Returns:
        Service statistics
    """
    return {
        "connections": {
            "total": connection_manager.get_total_connections(),
            "users": len(connection_manager.get_connected_users())
        },
        "sequences": sequence_tracker.get_stats()
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)
