"""
User preferences management endpoints.
"""

import logging
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional

logger = logging.getLogger(__name__)

router = APIRouter()


class PreferencesResponse(BaseModel):
    """Preferences response model."""
    success: bool
    preferences: Optional[dict] = None
    message: Optional[str] = None


class UpdatePreferencesRequest(BaseModel):
    """Update preferences request model."""
    notificationEnabled: Optional[bool] = None
    emailNotifications: Optional[bool] = None
    reminderMinutesBefore: Optional[int] = None
    defaultPriority: Optional[str] = None
    timezone: Optional[str] = None


@router.get("/api/v1/preferences/{user_id}", response_model=PreferencesResponse)
async def get_preferences(
    user_id: str,
    dapr_client=Depends(lambda: None)  # Will be injected in main.py
):
    """
    Get user preferences.

    Args:
        user_id: User ID

    Returns:
        User preferences
    """
    try:
        from shared.utils.state_keys import generate_preferences_key

        # Get preferences from state store
        prefs_key = generate_preferences_key(user_id)
        preferences = await dapr_client.get_state(prefs_key)

        # Return default preferences if not found
        if not preferences:
            preferences = {
                "userId": user_id,
                "notificationEnabled": True,
                "emailNotifications": False,
                "reminderMinutesBefore": 15,
                "defaultPriority": "medium",
                "timezone": "UTC"
            }

        return PreferencesResponse(
            success=True,
            preferences=preferences,
            message="Preferences retrieved successfully"
        )

    except Exception as e:
        logger.error(f"Error getting preferences: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting preferences: {str(e)}")


@router.put("/api/v1/preferences/{user_id}", response_model=PreferencesResponse)
async def update_preferences(
    user_id: str,
    request: UpdatePreferencesRequest,
    dapr_client=Depends(lambda: None)
):
    """
    Update user preferences.

    Args:
        user_id: User ID
        request: Preferences update request

    Returns:
        Updated preferences
    """
    try:
        from shared.utils.state_keys import generate_preferences_key
        from datetime import datetime

        # Get existing preferences
        prefs_key = generate_preferences_key(user_id)
        preferences = await dapr_client.get_state(prefs_key)

        # Initialize if not exists
        if not preferences:
            preferences = {
                "userId": user_id,
                "notificationEnabled": True,
                "emailNotifications": False,
                "reminderMinutesBefore": 15,
                "defaultPriority": "medium",
                "timezone": "UTC",
                "createdAt": datetime.utcnow().isoformat() + "Z"
            }

        # Update fields
        if request.notificationEnabled is not None:
            preferences["notificationEnabled"] = request.notificationEnabled
        if request.emailNotifications is not None:
            preferences["emailNotifications"] = request.emailNotifications
        if request.reminderMinutesBefore is not None:
            preferences["reminderMinutesBefore"] = request.reminderMinutesBefore
        if request.defaultPriority is not None:
            preferences["defaultPriority"] = request.defaultPriority
        if request.timezone is not None:
            preferences["timezone"] = request.timezone

        preferences["updatedAt"] = datetime.utcnow().isoformat() + "Z"

        # Save to state store
        await dapr_client.save_state(prefs_key, preferences)

        logger.info(f"Preferences updated for user: {user_id}")

        return PreferencesResponse(
            success=True,
            preferences=preferences,
            message="Preferences updated successfully"
        )

    except Exception as e:
        logger.error(f"Error updating preferences: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error updating preferences: {str(e)}")
