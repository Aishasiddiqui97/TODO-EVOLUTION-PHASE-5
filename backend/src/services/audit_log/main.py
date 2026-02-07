"""
Audit Log Service for Event-Driven Todo Chatbot.

Maintains immutable audit trail of all task events for compliance and debugging.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging

from .services.audit_service import AuditService
from .handlers.task_events import TaskEventsHandler
from .routes import audit, health

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global instances
audit_service = AuditService(dapr_http_port=3500)
task_events_handler = TaskEventsHandler(audit_service)

# Create FastAPI app
app = FastAPI(
    title="Audit Log Service",
    description="Immutable audit trail for task events",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize audit router with dependencies
audit.init_audit_router(audit_service)

# Include routers
app.include_router(audit.router, tags=["audit"])
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
            return await task_events_handler.handle_task_created(event)
        elif event_type == "task.updated":
            return await task_events_handler.handle_task_updated(event)
        elif event_type == "task.completed":
            return await task_events_handler.handle_task_completed(event)
        elif event_type == "task.deleted":
            return await task_events_handler.handle_task_deleted(event)
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
        "service": "audit-log",
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
        "service": "audit-log",
        "status": "operational",
        "features": [
            "Immutable audit trail",
            "Event logging",
            "Query API",
            "User statistics"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8005)
