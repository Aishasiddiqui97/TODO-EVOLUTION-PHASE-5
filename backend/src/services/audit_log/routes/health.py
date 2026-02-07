"""
Health check endpoints for Audit Log service.

Provides health, liveness, and readiness endpoints for Kubernetes.
"""

from fastapi import APIRouter
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
async def health_check() -> Dict[str, Any]:
    """
    Basic health check endpoint.

    Returns:
        Health status
    """
    return {
        "status": "healthy",
        "service": "audit-log"
    }


@router.get("/health/live")
async def liveness_check() -> Dict[str, Any]:
    """
    Kubernetes liveness probe endpoint.

    Returns:
        Liveness status
    """
    return {
        "status": "alive",
        "service": "audit-log"
    }


@router.get("/health/ready")
async def readiness_check() -> Dict[str, Any]:
    """
    Kubernetes readiness probe endpoint.

    Returns:
        Readiness status
    """
    # Could add checks for Dapr availability, state store connectivity, etc.
    return {
        "status": "ready",
        "service": "audit-log"
    }
