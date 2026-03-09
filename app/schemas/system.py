from typing import Any

from pydantic import BaseModel


class SystemAction(BaseModel):
    action: str
    payload: dict[str, Any] | None = {}

class MutableSettingsSchema(BaseModel):
    DATABASE_PATH: str | None = None
    GEMINI_API_KEY_ANALYSIS: str | None = None
    GEMINI_API_KEY_CHAT: str | None = None
    VOICE_ASSISTANT_ENABLED: bool = True
    SMTP_SERVER: str | None = None
    SMTP_PORT: int = 587
    SMTP_USERNAME: str | None = None
    SMTP_PASSWORD: str | None = None
    ALERT_THRESHOLD_DAYS: int = 60
    ALERT_THRESHOLD_DAYS_VISITE: int = 30

class SystemStatusSchema(BaseModel):
    status: str
    version: str
    database_locked: bool
    lock_owner: str | None = None
