from datetime import datetime
from pydantic import BaseModel, ConfigDict

class AuditLogSchema(BaseModel):
    id: int
    user_id: int | None = None
    username: str
    action: str
    category: str | None = None
    details: str | None = None
    timestamp: datetime
    ip_address: str | None = None
    user_agent: str | None = None
    geolocation: str | None = None
    severity: str | None = "LOW"
    device_id: str | None = None
    changes: str | None = None
    model_config = ConfigDict(from_attributes=True)
