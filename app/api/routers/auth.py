from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core import security
from app.core.config import settings
from app.schemas.schemas import Token, User
from app.api import deps
from app.db.models import BlacklistedToken

router = APIRouter()

@router.post("/logout")
def logout(
    token: str = Depends(deps.oauth2_scheme),
    current_user: User = Depends(deps.get_current_user),
    db: Session = Depends(get_db)
):
    """
    Invalidate the current token by adding it to the blacklist.
    """
    # Check again to be safe, though unique constraint handles it
    if not db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first():
        try:
            blacklist_entry = BlacklistedToken(token=token)
            db.add(blacklist_entry)
            db.commit()
        except Exception:
            db.rollback()
            # If it failed, it's likely already blacklisted or race condition.
            # We treat it as success (idempotent).
            pass

    return {"message": "Successfully logged out"}

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = db.query(deps.User).filter(deps.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "account_name": user.account_name,
        "is_admin": user.is_admin
    }

@router.get("/me", response_model=User)
def read_users_me(current_user: deps.User = Depends(deps.get_current_user)):
    """
    Fetch the current logged in user.
    """
    return current_user
