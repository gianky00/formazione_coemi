from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict

class UserBase(BaseModel):
    username: str
    account_name: str | None = None
    gender: str | None = None
    is_admin: bool = False

class UserCreateSchema(UserBase):
    password: str | None = None

class UserPasswordUpdateSchema(BaseModel):
    old_password: str
    new_password: str
    confirm_password: str

class UserUpdateSchema(BaseModel):
    username: str | None = None
    account_name: str | None = None
    password: str | None = None
    gender: str | None = None
    is_admin: bool | None = None

class UserSchema(UserBase):
    id: int
    last_login: datetime | None = None
    previous_login: datetime | None = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str
    account_name: str | None = None
    gender: str | None = None
    is_admin: bool
    previous_login: datetime | None = None
    read_only: bool = False
    lock_owner: dict[str, Any] | None = None
    require_password_change: bool = False

class TokenData(BaseModel):
    username: str | None = None
