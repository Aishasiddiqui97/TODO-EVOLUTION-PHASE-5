"""
Chat API Main Application for Event-Driven Todo Chatbot.

FastAPI application that provides REST endpoints and integrates with OpenAI Agents SDK.
"""

import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .shared.utils.logging import setup_logging
from .shared.dapr_client.client import DaprClientWrapper

# Setup structured logging
setup_logging()
logger = logging.getLogger(__name__)

# Environment variables
DAPR_HTTP_PORT = os.getenv("DAPR_HTTP_PORT", "3500")
DAPR_GRPC_PORT = os.getenv("DAPR_GRPC_PORT", "50001")
APP_PORT = int(os.getenv("APP_PORT", "8001"))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """
    Application lifespan manager.

    Handles startup and shutdown events.
    """
    # Startup
    logger.info("Starting Chat API service", extra={
        "dapr_http_port": DAPR_HTTP_PORT,
        "dapr_grpc_port": DAPR_GRPC_PORT,
        "app_port": APP_PORT
    })

    # Verify Dapr connection
    try:
        dapr_client = DaprClientWrapper()
        logger.info("Dapr client initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Dapr client: {e}", exc_info=True)
        raise

    # Verify OpenAI API key
    if not OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set - AI features will not work")

    yield

    # Shutdown
    logger.info("Shutting down Chat API service")


# Create FastAPI application
app = FastAPI(
    title="Event-Driven Todo Chatbot - Chat API",
    description="REST API for AI-powered task management with event-driven architecture",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.
    """
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "path": request.url.path,
            "method": request.method
        }
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "internal_server_error",
            "message": "An unexpected error occurred"
        }
    )


@app.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes liveness/readiness probes.
    """
    return {
        "status": "healthy",
        "service": "chat-api",
        "version": "1.0.0"
    }


@app.get("/")
async def root():
    """
    Root endpoint with API information.
    """
    return {
        "service": "chat-api",
        "version": "1.0.0",
        "description": "Event-Driven Todo Chatbot API",
        "endpoints": {
            "health": "/health",
            "chat": "/api/v1/chat",
            "tasks": "/api/v1/tasks",
            "preferences": "/api/v1/preferences"
        }
    }


# Include routers
from .api.routes.tasks import router as tasks_router
from .api.routes.chat import router as chat_router
from .api.routes.preferences import router as preferences_router
from .api.routes.simple_chat import router as simple_chat_router

app.include_router(tasks_router)
app.include_router(chat_router)
app.include_router(preferences_router)
app.include_router(simple_chat_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=APP_PORT,
        log_level="info",
        reload=False
    )
