"""
Health check endpoint for Chat API service.
"""

from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "chat-api",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }


@router.get("/")
async def root():
    """
    Root endpoint with API information.

    Returns:
        API information
    """
    return {
        "service": "Event-Driven Todo Chatbot - Chat API",
        "version": "1.0.0",
        "description": "Natural language task management with AI",
        "endpoints": {
            "health": "/health",
            "chat": "/api/v1/chat",
            "tasks": "/api/v1/tasks",
            "preferences": "/api/v1/preferences"
        }
    }
