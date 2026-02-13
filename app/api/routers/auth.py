from datetime import timedelta
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.core.db_security import db_security
from app.db.models import User
from app.db.session import get_db
from app.schemas.schemas import Token
from app.utils.audit import log_security_action

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=Token)
def login_access_token(
    db: Annotated[Session, Depends(get_db)],
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Any:
    """OAuth2 compatible token login, get an access token for future requests."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        log_security_action(
            db,
            None,
            "LOGIN_FAILED",
            f"Fallito login per {form_data.username}",
            category="AUTH",
            severity="MEDIUM",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 1. Acquire session lock (Try to become the Writer)
    success, owner_info = db_security.acquire_session_lock({"username": user.username})

    # 2. Generate Access Token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    token = security.create_access_token({"sub": user.username}, expires_delta=access_token_expires)

    log_security_action(db, user, "LOGIN_SUCCESS", "Login effettuato con successo", category="AUTH")

    # 3. Return full Token schema
    return {
        "access_token": token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "account_name": user.account_name,
        "gender": user.gender,
        "is_admin": user.is_admin,
        "previous_login": user.previous_login,
        "read_only": not success,
        "lock_owner": owner_info,
        "require_password_change": False,  # Can be expanded
    }


@router.get("/me", response_model=Any)
def read_user_me(
    current_user: Annotated[User, Depends(deps.get_current_user)],
) -> Any:
    """Ritorna l'utente corrente autenticato."""
    return current_user
