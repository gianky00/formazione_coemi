from pydantic import BaseModel
from typing import Optional, Dict, Any

class SystemAction(BaseModel):
    action: str
    payload: Optional[Dict[str, Any]] = {}
