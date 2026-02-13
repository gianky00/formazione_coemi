from typing import Any

from pydantic import BaseModel


class SystemAction(BaseModel):
    action: str
    payload: dict[str, Any] | None = {}
