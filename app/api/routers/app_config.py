from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from app.api.deps import get_current_active_admin, check_write_permission, get_current_user
from app.core.config import settings, get_user_data_dir
import logging
from pathlib import Path

router = APIRouter()

class AppConfigSchema(BaseModel):
    github_token: str
    repo_owner: str
    repo_name: str

class MutableSettingsSchema(BaseModel):
    """Pydantic model for validating incoming mutable settings updates."""
    FIRST_RUN_ADMIN_PASSWORD: Optional[str] = Field(None, min_length=4)
    GEMINI_API_KEY_ANALYSIS: Optional[str] = None
    GEMINI_API_KEY_CHAT: Optional[str] = None
    VOICE_ASSISTANT_ENABLED: Optional[bool] = None
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: Optional[int] = Field(None, gt=0, le=65535)
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_RECIPIENTS_TO: Optional[str] = None
    EMAIL_RECIPIENTS_CC: Optional[str] = None
    ALERT_THRESHOLD_DAYS: Optional[int] = Field(None, ge=1)
    ALERT_THRESHOLD_DAYS_VISITE: Optional[int] = Field(None, ge=1)

@router.get("/config/updater", response_model=AppConfigSchema)
async def get_updater_config():
    """
    Provides the necessary configuration for the client-side license updater.
    This endpoint is public.
    """
    return AppConfigSchema(
        github_token=settings.LICENSE_GITHUB_TOKEN,
        repo_owner=settings.LICENSE_REPO_OWNER,
        repo_name=settings.LICENSE_REPO_NAME
    )

@router.get("/config/paths", response_model=Dict[str, str])
async def get_config_paths(
    current_user: dict = Depends(get_current_user)
):
    """
    Returns the configured database path and the default user data directory.
    Accessible to any authenticated user.
    """
    default_dir = get_user_data_dir()
    db_path = settings.DATABASE_PATH

    final_path = default_dir
    if db_path and Path(db_path).is_dir():
         final_path = Path(db_path)

    return {
        "database_path": str(final_path),
        "default_path": str(default_dir)
    }

@router.get("/config", response_model=Dict[str, Any])
async def get_mutable_config(
    current_user: dict = Depends(get_current_active_admin)
):
    """
    Retrieves the current user-configurable settings.
    Requires admin privileges.
    """
    return settings.mutable.as_dict()

@router.put("/config", status_code=status.HTTP_204_NO_CONTENT)
async def update_mutable_config(
    new_settings: MutableSettingsSchema,
    current_user: dict = Depends(get_current_active_admin),
    write_permission: None = Depends(check_write_permission)
):
    """
    Updates user-configurable settings and saves them.
    Requires admin privileges.
    """
    try:
        # Get a dictionary of the fields that are actually present in the request
        update_data = new_settings.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Request body cannot be empty."
            )

        logging.info(f"User '{current_user.username}' updating settings with: {update_data.keys()}")

        # Save the updated settings
        settings.save_mutable_settings(update_data)

        return None # Return 204 No Content on success

    except HTTPException:
        # Re-raise HTTPException to let FastAPI handle it
        raise
    except Exception as e:
        logging.error(f"Failed to update settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while saving the settings."
        )
