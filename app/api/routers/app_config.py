import logging
from pathlib import Path
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field

from app.api import deps
from app.core.config import get_user_data_dir, settings
from app.db.models import User

router = APIRouter(prefix="/app_config", tags=["app_config"])


class AppConfigSchema(BaseModel):
    github_token: str
    repo_owner: str
    repo_name: str


class MutableSettingsSchema(BaseModel):
    """Pydantic model for validating incoming mutable settings updates."""

    FIRST_RUN_ADMIN_PASSWORD: str | None = Field(None, min_length=4)
    GEMINI_API_KEY_ANALYSIS: str | None = None
    GEMINI_API_KEY_CHAT: str | None = None
    VOICE_ASSISTANT_ENABLED: bool | None = None
    SMTP_HOST: str | None = None
    SMTP_PORT: int | None = Field(None, gt=0, le=65535)
    SMTP_USER: str | None = None
    SMTP_PASSWORD: str | None = None
    EMAIL_RECIPIENTS_TO: str | None = None
    EMAIL_RECIPIENTS_CC: str | None = None
    ALERT_THRESHOLD_DAYS: int | None = Field(None, ge=1)
    ALERT_THRESHOLD_DAYS_VISITE: int | None = Field(None, ge=1)

    # Extra fields sent by frontend that we must ignore to avoid 400 Bad Request
    account_name: str | None = None
    gender: str | None = None


@router.get("/config/updater", response_model=AppConfigSchema)
async def get_updater_config() -> Any:
    """
    Provides the necessary configuration for the client-side license updater.
    """
    return AppConfigSchema(
        github_token=settings.LICENSE_GITHUB_TOKEN,
        repo_owner=settings.LICENSE_REPO_OWNER,
        repo_name=settings.LICENSE_REPO_NAME,
    )


@router.get("/config/paths", response_model=dict[str, str])
async def get_config_paths(
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Any:
    """
    Returns the configured database path and the default user data directory.
    """
    default_dir = get_user_data_dir()
    db_path = settings.DATABASE_PATH

    final_path = default_dir
    if db_path:
        db_path_obj = Path(db_path)
        if db_path_obj.is_dir():
            final_path = db_path_obj
        elif db_path_obj.is_file() or db_path_obj.suffix:
            final_path = db_path_obj.parent

    return {"database_path": str(final_path), "default_path": str(default_dir)}


@router.get("/config", response_model=dict[str, Any])
async def get_mutable_config(
    current_user: Annotated[User, Depends(deps.get_current_active_admin)],
) -> Any:
    """
    Retrieves the current user-configurable settings.
    """
    return settings.mutable.as_dict()


@router.put("/config", status_code=status.HTTP_204_NO_CONTENT)
async def update_mutable_config(
    new_settings: MutableSettingsSchema,
    current_user: Annotated[User, Depends(deps.get_current_active_admin)],
    write_permission: Annotated[None, Depends(deps.check_write_permission)],
) -> None:
    """
    Updates user-configurable settings and saves them.
    """
    try:
        update_data = new_settings.model_dump(exclude_unset=True)

        filtered_data = {
            k: v for k, v in update_data.items() if k not in ["account_name", "gender"]
        }

        if not filtered_data:
            if "account_name" in update_data or "gender" in update_data:
                return

            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Request body cannot be empty."
            )

        logging.info(
            f"User '{current_user.username}' updating settings with: {filtered_data.keys()}"
        )

        settings.save_mutable_settings(filtered_data)

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Failed to update settings: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred while saving the settings.",
        ) from e
