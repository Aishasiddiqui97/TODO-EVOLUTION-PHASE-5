"""
Chat API Service - Main Application

Event-driven task management with AI-powered natural language interface.
"""

import logging
import os
import sys
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

# Add parent directories to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))

from shared.dapr_client.client import DaprClient
from shared.events.publisher import EventPublisher
from shared.utils.logging import setup_logging
from services.task_service import TaskService
from services.conversation_service import ConversationService
from ai.agent import AIAgent
from mcp.server import MCPServer

# Import routes
from routes import health, chat, tasks, preferences

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

# Global service instances
dapr_client = None
event_publisher = None
task_service = None
conversation_service = None
ai_agent = None
mcp_server = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Initializes services on startup and cleans up on shutdown.
    """
    global dapr_client, event_publisher, task_service, conversation_service, ai_agent, mcp_server

    logger.info("Starting Chat API service...")

    try:
        # Initialize Dapr client
        dapr_http_port = int(os.getenv("DAPR_HTTP_PORT", "3500"))
        dapr_client = DaprClient(dapr_http_port=dapr_http_port)
        logger.info(f"Dapr client initialized (port: {dapr_http_port})")

        # Initialize event publisher
        event_publisher = EventPublisher(dapr_client=dapr_client)
        logger.info("Event publisher initialized")

        # Initialize services
        task_service = TaskService(
            dapr_client=dapr_client,
            event_publisher=event_publisher
        )
        conversation_service = ConversationService(dapr_client=dapr_client)
        logger.info("Services initialized")

        # Initialize AI agent
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            logger.warning("OPENAI_API_KEY not set - AI features will not work")
        ai_agent = AIAgent(api_key=openai_api_key)
        logger.info("AI agent initialized")

        # Initialize MCP server
        mcp_server = MCPServer(
            task_service=task_service,
            conversation_service=conversation_service
        )
        logger.info("MCP server initialized")

        logger.info("Chat API service started successfully")

        yield

    except Exception as e:
        logger.error(f"Error during startup: {e}", exc_info=True)
        raise

    finally:
        logger.info("Shutting down Chat API service...")


# Create FastAPI application
app = FastAPI(
    title="Event-Driven Todo Chatbot - Chat API",
    description="Natural language task management with AI",
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


# Dependency injection for routes
def get_dapr_client():
    """Get Dapr client instance."""
    return dapr_client


def get_task_service():
    """Get task service instance."""
    return task_service


def get_conversation_service():
    """Get conversation service instance."""
    return conversation_service


def get_ai_agent():
    """Get AI agent instance."""
    return ai_agent


def get_mcp_server():
    """Get MCP server instance."""
    return mcp_server


# Override route dependencies
app.dependency_overrides[lambda: None] = get_task_service

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(chat.router, tags=["chat"])
app.include_router(tasks.router, tags=["tasks"])
app.include_router(preferences.router, tags=["preferences"])


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """
    Global exception handler for unhandled errors.

    Args:
        request: FastAPI request
        exc: Exception

    Returns:
        JSON error response
    """
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc),
            "path": str(request.url)
        }
    )


# Middleware for dependency injection in routes
@app.middleware("http")
async def inject_dependencies(request: Request, call_next):
    """
    Middleware to inject service dependencies into route handlers.

    Args:
        request: FastAPI request
        call_next: Next middleware/handler

    Returns:
        Response
    """
    # Store services in request state for access in routes
    request.state.dapr_client = dapr_client
    request.state.task_service = task_service
    request.state.conversation_service = conversation_service
    request.state.ai_agent = ai_agent
    request.state.mcp_server = mcp_server

    response = await call_next(request)
    return response


# Update route dependencies to use request state
from functools import wraps


def inject_service_dependencies(func):
    """Decorator to inject service dependencies from request state."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        # Get request from kwargs
        request = kwargs.get('request')
        if request:
            # Inject services from request state
            if 'task_service' in kwargs and kwargs['task_service'] is None:
                kwargs['task_service'] = request.state.task_service
            if 'conversation_service' in kwargs and kwargs['conversation_service'] is None:
                kwargs['conversation_service'] = request.state.conversation_service
            if 'ai_agent' in kwargs and kwargs['ai_agent'] is None:
                kwargs['ai_agent'] = request.state.ai_agent
            if 'mcp_server' in kwargs and kwargs['mcp_server'] is None:
                kwargs['mcp_server'] = request.state.mcp_server
            if 'dapr_client' in kwargs and kwargs['dapr_client'] is None:
                kwargs['dapr_client'] = request.state.dapr_client

        return await func(*args, **kwargs)

    return wrapper


# Apply decorator to route handlers
for route in app.routes:
    if hasattr(route, 'endpoint'):
        route.endpoint = inject_service_dependencies(route.endpoint)


if __name__ == "__main__":
    import uvicorn

    port = int(os.getenv("PORT", "8001"))
    host = os.getenv("HOST", "0.0.0.0")

    logger.info(f"Starting Chat API on {host}:{port}")

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
