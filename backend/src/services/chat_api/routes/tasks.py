"""
Task management REST API endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
from typing import Optional, List

logger = logging.getLogger(__name__)

router = APIRouter()


class CreateTaskRequest(BaseModel):
    """Create task request model."""
    title: str
    description: Optional[str] = None
    priority: str = "medium"
    dueDate: Optional[str] = None
    dueTime: Optional[str] = None
    tags: Optional[List[str]] = None
    recurrencePattern: Optional[str] = None
    userId: str


class UpdateTaskRequest(BaseModel):
    """Update task request model."""
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    dueDate: Optional[str] = None
    dueTime: Optional[str] = None
    tags: Optional[List[str]] = None
    status: Optional[str] = None


class TaskResponse(BaseModel):
    """Task response model."""
    success: bool
    task: Optional[dict] = None
    message: Optional[str] = None


class TaskListResponse(BaseModel):
    """Task list response model."""
    success: bool
    tasks: List[dict]
    count: int
    message: Optional[str] = None


@router.post("/api/v1/tasks", response_model=TaskResponse)
async def create_task(
    request: CreateTaskRequest,
    task_service=Depends(lambda: None)  # Will be injected in main.py
):
    """
    Create a new task.

    Args:
        request: Task creation request

    Returns:
        Created task
    """
    try:
        task = await task_service.create_task(
            user_id=request.userId,
            title=request.title,
            description=request.description,
            priority=request.priority,
            due_date=request.dueDate,
            due_time=request.dueTime,
            tags=request.tags,
            recurrence_pattern=request.recurrencePattern
        )

        return TaskResponse(
            success=True,
            task=task,
            message=f"Task '{task['title']}' created successfully"
        )

    except Exception as e:
        logger.error(f"Error creating task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


@router.get("/api/v1/tasks", response_model=TaskListResponse)
async def list_tasks(
    userId: str = Query(..., description="User ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    tags: Optional[str] = Query(None, description="Filter by tags (comma-separated)"),
    task_service=Depends(lambda: None)
):
    """
    List tasks for a user with optional filters.

    Args:
        userId: User ID
        status: Optional status filter
        priority: Optional priority filter
        tags: Optional tags filter (comma-separated)

    Returns:
        List of tasks
    """
    try:
        # Parse tags if provided
        tag_list = tags.split(",") if tags else None

        tasks = await task_service.list_tasks(
            user_id=userId,
            status=status,
            priority=priority,
            tags=tag_list
        )

        return TaskListResponse(
            success=True,
            tasks=tasks,
            count=len(tasks),
            message=f"Found {len(tasks)} task(s)"
        )

    except Exception as e:
        logger.error(f"Error listing tasks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error listing tasks: {str(e)}")


@router.get("/api/v1/tasks/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    task_service=Depends(lambda: None)
):
    """
    Get a specific task by ID.

    Args:
        task_id: Task ID

    Returns:
        Task details
    """
    try:
        task = await task_service.get_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return TaskResponse(
            success=True,
            task=task,
            message="Task retrieved successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting task: {str(e)}")


@router.put("/api/v1/tasks/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    request: UpdateTaskRequest,
    task_service=Depends(lambda: None)
):
    """
    Update a task.

    Args:
        task_id: Task ID
        request: Update request

    Returns:
        Updated task
    """
    try:
        # Build updates dictionary
        updates = {}
        if request.title is not None:
            updates["title"] = request.title
        if request.description is not None:
            updates["description"] = request.description
        if request.priority is not None:
            updates["priority"] = request.priority
        if request.dueDate is not None:
            updates["dueDate"] = request.dueDate
        if request.dueTime is not None:
            updates["dueTime"] = request.dueTime
        if request.tags is not None:
            updates["tags"] = request.tags
        if request.status is not None:
            updates["status"] = request.status

        task = await task_service.update_task(task_id, updates)

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return TaskResponse(
            success=True,
            task=task,
            message=f"Task '{task['title']}' updated successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating task: {str(e)}")


@router.patch("/api/v1/tasks/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    task_service=Depends(lambda: None)
):
    """
    Mark a task as completed.

    Args:
        task_id: Task ID

    Returns:
        Completed task
    """
    try:
        task = await task_service.complete_task(task_id)

        if not task:
            raise HTTPException(status_code=404, detail="Task not found")

        return TaskResponse(
            success=True,
            task=task,
            message=f"Task '{task['title']}' marked as completed"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error completing task: {str(e)}")


@router.delete("/api/v1/tasks/{task_id}")
async def delete_task(
    task_id: str,
    task_service=Depends(lambda: None)
):
    """
    Delete a task.

    Args:
        task_id: Task ID

    Returns:
        Success message
    """
    try:
        success = await task_service.delete_task(task_id)

        if not success:
            raise HTTPException(status_code=404, detail="Task not found")

        return {
            "success": True,
            "message": "Task deleted successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error deleting task: {str(e)}")


@router.post("/api/v1/tasks/search", response_model=TaskListResponse)
async def search_tasks(
    request: dict,
    task_service=Depends(lambda: None)
):
    """
    Search tasks using natural language query.

    Args:
        request: Search request with query and userId

    Returns:
        List of matching tasks
    """
    try:
        query = request.get("query")
        user_id = request.get("userId")

        if not query or not user_id:
            raise HTTPException(status_code=400, detail="query and userId are required")

        # Import search function
        from mcp.tools.search_tasks import search_tasks as search_func
        result = await search_func(userId=user_id, query=query)

        tasks = result.get("tasks", [])

        return TaskListResponse(
            success=True,
            tasks=tasks,
            count=len(tasks),
            message=result.get("message", f"Found {len(tasks)} task(s)")
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching tasks: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error searching tasks: {str(e)}")
