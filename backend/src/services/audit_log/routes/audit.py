"""
Audit log query endpoints for Audit Log service.

Provides REST API for querying audit logs.
"""

from fastapi import APIRouter, Query
from typing import Optional
import logging

from ..services.audit_service import AuditService

logger = logging.getLogger(__name__)

router = APIRouter()

# Will be injected by main app
audit_service: Optional[AuditService] = None


def init_audit_router(service: AuditService):
    """
    Initialize the audit router with dependencies.

    Args:
        service: Audit service instance
    """
    global audit_service
    audit_service = service


@router.get("/audit/user/{user_id}")
async def get_user_audit_logs(
    user_id: str,
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of entries"),
    offset: int = Query(0, ge=0, description="Number of entries to skip"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    task_id: Optional[str] = Query(None, description="Filter by task ID"),
    start_date: Optional[str] = Query(None, description="Filter by start date (ISO format)"),
    end_date: Optional[str] = Query(None, description="Filter by end date (ISO format)")
):
    """
    Get audit logs for a user.

    Args:
        user_id: User ID
        limit: Maximum number of entries to return
        offset: Number of entries to skip
        event_type: Filter by event type (task.created, task.updated, etc.)
        task_id: Filter by task ID
        start_date: Filter by start date (ISO format)
        end_date: Filter by end date (ISO format)

    Returns:
        Audit logs with pagination info
    """
    if not audit_service:
        return {"error": "Service not initialized"}

    result = await audit_service.get_user_audit_logs(
        user_id=user_id,
        limit=limit,
        offset=offset,
        event_type=event_type,
        task_id=task_id,
        start_date=start_date,
        end_date=end_date
    )

    return result


@router.get("/audit/task/{task_id}")
async def get_task_audit_logs(
    task_id: str,
    user_id: str = Query(..., description="User ID for authorization")
):
    """
    Get all audit logs for a specific task.

    Args:
        task_id: Task ID
        user_id: User ID for authorization

    Returns:
        Audit logs for the task
    """
    if not audit_service:
        return {"error": "Service not initialized"}

    result = await audit_service.get_task_audit_logs(
        task_id=task_id,
        user_id=user_id
    )

    return result


@router.get("/audit/entry/{audit_id}")
async def get_audit_log_entry(audit_id: str):
    """
    Get a specific audit log entry by ID.

    Args:
        audit_id: Audit log entry ID

    Returns:
        Audit log entry or 404
    """
    if not audit_service:
        return {"error": "Service not initialized"}

    entry = await audit_service.get_audit_log_by_id(audit_id)

    if entry:
        return entry
    else:
        return {"error": "Audit log entry not found"}


@router.get("/audit/stats/{user_id}")
async def get_user_audit_stats(user_id: str):
    """
    Get audit statistics for a user.

    Args:
        user_id: User ID

    Returns:
        Statistics about user's audit logs
    """
    if not audit_service:
        return {"error": "Service not initialized"}

    # Get all logs to calculate stats
    result = await audit_service.get_user_audit_logs(
        user_id=user_id,
        limit=10000
    )

    if not result.get("success"):
        return {"error": result.get("error", "Failed to retrieve logs")}

    logs = result.get("logs", [])

    # Calculate statistics
    event_type_counts = {}
    task_counts = {}

    for log in logs:
        event_type = log.get("eventType", "unknown")
        task_id = log.get("taskId")

        event_type_counts[event_type] = event_type_counts.get(event_type, 0) + 1

        if task_id:
            task_counts[task_id] = task_counts.get(task_id, 0) + 1

    return {
        "userId": user_id,
        "totalEvents": len(logs),
        "eventTypeCounts": event_type_counts,
        "uniqueTasks": len(task_counts),
        "mostActiveTask": max(task_counts.items(), key=lambda x: x[1])[0] if task_counts else None
    }
