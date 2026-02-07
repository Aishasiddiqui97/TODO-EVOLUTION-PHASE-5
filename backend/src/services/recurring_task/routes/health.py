"""
Health check endpoint for Recurring Task Service.

Provides health status for Kubernetes liveness and readiness probes.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check():
    """
    Health check endpoint for Kubernetes liveness/readiness probes.

    Returns:
        Dict with service health status
    """
    return {
        "status": "healthy",
        "service": "recurring-task",
        "version": "1.0.0"
    }


@router.get("/health/live")
async def liveness_check():
    """
    Liveness probe endpoint.

    Indicates if the service is running and should not be restarted.

    Returns:
        Dict with liveness status
    """
    return {
        "status": "alive",
        "service": "recurring-task"
    }


@router.get("/health/ready")
async def readiness_check():
    """
    Readiness probe endpoint.

    Indicates if the service is ready to accept traffic.

    Returns:
        Dict with readiness status
    """
    # In production, this could check:
    # - Dapr sidecar connectivity
    # - Required dependencies availability
    # - Service initialization completion

    return {
        "status": "ready",
        "service": "recurring-task"
    }
