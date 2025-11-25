from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.api.deps import get_current_user
from app.core.config import settings

router = APIRouter()

class AppConfigSchema(BaseModel):
    github_token: str
    repo_owner: str
    repo_name: str

@router.get("/config/updater", response_model=AppConfigSchema)
async def get_updater_config(current_user: dict = Depends(get_current_user)):
    """
    Provides the necessary configuration for the client-side license updater.
    This endpoint requires authentication.
    """
    return AppConfigSchema(
        github_token=settings.LICENSE_GITHUB_TOKEN,
        repo_owner=settings.LICENSE_REPO_OWNER,
        repo_name=settings.LICENSE_REPO_NAME
    )
