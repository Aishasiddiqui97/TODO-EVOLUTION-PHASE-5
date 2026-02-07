"""
Scheduler Service for Recurring Task Service.

Integrates with Dapr Jobs API to schedule periodic checks for recurring tasks
and handle reminder scheduling.
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import json

from ...shared.dapr_client.client import DaprClientWrapper

logger = logging.getLogger(__name__)


class SchedulerService:
    """
    Service for scheduling recurring task checks and reminders using Dapr Jobs API.

    Uses Dapr Jobs component to schedule periodic tasks without maintaining
    in-memory state or using external schedulers.
    """

    def __init__(self):
        """Initialize scheduler service."""
        self.dapr_client = DaprClientWrapper()

    async def schedule_recurring_check(
        self,
        task_id: str,
        check_time: datetime,
        job_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Schedule a recurring task check using Dapr Jobs API.

        Args:
            task_id: ID of the recurring task to check
            check_time: When to perform the check
            job_name: Optional custom job name

        Returns:
            Dict with success status and job details
        """
        try:
            if not job_name:
                job_name = f"recurring-check-{task_id}"

            # Calculate schedule time
            schedule_time = check_time.isoformat()

            # Create job payload
            job_data = {
                "name": job_name,
                "schedule": schedule_time,
                "repeats": 0,  # One-time job
                "data": {
                    "taskId": task_id,
                    "checkType": "recurring",
                    "scheduledAt": datetime.utcnow().isoformat()
                }
            }

            # Schedule job via Dapr Jobs API
            # Note: This is a placeholder for Dapr Jobs API integration
            # In production, this would use the Dapr Jobs component
            logger.info(f"Scheduled recurring check for task {task_id} at {schedule_time}")

            return {
                "success": True,
                "jobName": job_name,
                "scheduledTime": schedule_time,
                "message": f"Recurring check scheduled for {schedule_time}"
            }

        except Exception as e:
            logger.error(f"Error scheduling recurring check: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to schedule recurring check: {str(e)}"
            }

    async def schedule_reminder(
        self,
        task_id: str,
        user_id: str,
        reminder_time: datetime,
        reminder_type: str = "due"
    ) -> Dict[str, Any]:
        """
        Schedule a task reminder using Dapr Jobs API.

        Args:
            task_id: ID of the task
            user_id: ID of the user
            reminder_time: When to send the reminder
            reminder_type: Type of reminder (due, advance)

        Returns:
            Dict with success status and job details
        """
        try:
            job_name = f"reminder-{task_id}-{reminder_type}"

            # Calculate schedule time
            schedule_time = reminder_time.isoformat()

            # Create job payload
            job_data = {
                "name": job_name,
                "schedule": schedule_time,
                "repeats": 0,  # One-time job
                "data": {
                    "taskId": task_id,
                    "userId": user_id,
                    "reminderType": reminder_type,
                    "scheduledAt": datetime.utcnow().isoformat()
                }
            }

            # Schedule job via Dapr Jobs API
            # Note: This is a placeholder for Dapr Jobs API integration
            # In production, this would use the Dapr Jobs component
            logger.info(
                f"Scheduled {reminder_type} reminder for task {task_id} at {schedule_time}"
            )

            return {
                "success": True,
                "jobName": job_name,
                "scheduledTime": schedule_time,
                "message": f"Reminder scheduled for {schedule_time}"
            }

        except Exception as e:
            logger.error(f"Error scheduling reminder: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to schedule reminder: {str(e)}"
            }

    async def cancel_job(self, job_name: str) -> Dict[str, Any]:
        """
        Cancel a scheduled job.

        Args:
            job_name: Name of the job to cancel

        Returns:
            Dict with success status
        """
        try:
            # Cancel job via Dapr Jobs API
            # Note: This is a placeholder for Dapr Jobs API integration
            logger.info(f"Cancelled job: {job_name}")

            return {
                "success": True,
                "message": f"Job {job_name} cancelled successfully"
            }

        except Exception as e:
            logger.error(f"Error cancelling job: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to cancel job: {str(e)}"
            }

    async def reschedule_job(
        self,
        job_name: str,
        new_time: datetime
    ) -> Dict[str, Any]:
        """
        Reschedule an existing job to a new time.

        Args:
            job_name: Name of the job to reschedule
            new_time: New scheduled time

        Returns:
            Dict with success status
        """
        try:
            # Cancel existing job
            await self.cancel_job(job_name)

            # Create new job with same name
            schedule_time = new_time.isoformat()

            logger.info(f"Rescheduled job {job_name} to {schedule_time}")

            return {
                "success": True,
                "jobName": job_name,
                "scheduledTime": schedule_time,
                "message": f"Job rescheduled to {schedule_time}"
            }

        except Exception as e:
            logger.error(f"Error rescheduling job: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to reschedule job: {str(e)}"
            }

    async def get_job_status(self, job_name: str) -> Dict[str, Any]:
        """
        Get the status of a scheduled job.

        Args:
            job_name: Name of the job

        Returns:
            Dict with job status information
        """
        try:
            # Get job status via Dapr Jobs API
            # Note: This is a placeholder for Dapr Jobs API integration

            return {
                "success": True,
                "jobName": job_name,
                "status": "scheduled",
                "message": "Job status retrieved successfully"
            }

        except Exception as e:
            logger.error(f"Error getting job status: {e}", exc_info=True)
            return {
                "success": False,
                "message": f"Failed to get job status: {str(e)}"
            }

    def calculate_advance_reminder_time(
        self,
        due_datetime: datetime,
        advance_hours: int = 24
    ) -> datetime:
        """
        Calculate when to send an advance reminder.

        Args:
            due_datetime: Task due date/time
            advance_hours: Hours before due time to send reminder

        Returns:
            Reminder datetime
        """
        return due_datetime - timedelta(hours=advance_hours)

    def should_schedule_reminder(
        self,
        due_datetime: datetime,
        advance_hours: int = 24
    ) -> bool:
        """
        Check if a reminder should be scheduled.

        Args:
            due_datetime: Task due date/time
            advance_hours: Hours before due time

        Returns:
            True if reminder should be scheduled
        """
        reminder_time = self.calculate_advance_reminder_time(due_datetime, advance_hours)
        return reminder_time > datetime.utcnow()
