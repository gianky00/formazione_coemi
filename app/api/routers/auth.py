from datetime import timedelta, datetime
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core import security
from app.core.config import settings
from app.core.db_security import db_security
from app.schemas.schemas import Token, User
from app.api import deps
from app.db.models import BlacklistedToken, AuditLog
from app.utils.audit import log_security_action

router = APIRouter()

@router.post("/logout")
def logout(
    request: Request,
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
            log_security_action(db, current_user, "LOGOUT", "User logged out successfully", category="AUTH", request=request)
        except Exception:
            db.rollback()
            # If it failed, it's likely already blacklisted or race condition.
            # We treat it as success (idempotent).
            pass

    # Force DB Sync and Cleanup on logout to ensure data persistence and lock release
    try:
        db_security.cleanup()
    except Exception as e:
        print(f"Error cleaning up DB on logout: {e}")

    return {"message": "Successfully logged out"}

@router.post("/login", response_model=Token)
def login_access_token(
    request: Request,
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    user = db.query(deps.User).filter(deps.User.username == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        # ANOMALY DETECTION: Failed Login
        try:
            ip = request.client.host if request.client else "Unknown"
            # Brute force check: > 5 failures in last 10 minutes
            cutoff = datetime.utcnow() - timedelta(minutes=10)
            failed_count = db.query(AuditLog).filter(
                AuditLog.action == "LOGIN_FAILED",
                AuditLog.timestamp >= cutoff,
                AuditLog.ip_address == ip
            ).count()

            severity = "MEDIUM" # Single failure is Medium (warning) or Low. Let's say Medium to catch attention.
            if failed_count >= 5:
                severity = "CRITICAL"

            log_security_action(
                db,
                user if user else None, # Log user if known, else None
                "LOGIN_FAILED",
                details=f"Failed login attempt for username: {form_data.username}",
                category="AUTH",
                request=request,
                severity=severity
            )
        except Exception as e:
            print(f"Error logging failed login: {e}")

        raise HTTPException(status_code=400, detail="Incorrect email or password")

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    # Update last login
    old_last_login = user.last_login
    user.previous_login = old_last_login
    user.last_login = datetime.utcnow()
    db.commit()
    db.refresh(user)

    # Create Session Lock
    # This enforces single-user access upon successful login
    try:
        db_security.create_lock()
    except PermissionError as e:
        # Deny login if database is locked by another session
        raise HTTPException(status_code=409, detail=str(e))

    print(f"[DEBUG] Login success. Username: {user.username}, Previous Login: {user.previous_login}, New Last Login: {user.last_login}")

    log_security_action(db, user, "LOGIN", "User logged in successfully", category="AUTH", request=request)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": user.id,
        "username": user.username,
        "account_name": user.account_name,
        "is_admin": user.is_admin,
        "previous_login": user.previous_login
    }

@router.get("/me", response_model=User)
def read_users_me(current_user: deps.User = Depends(deps.get_current_user)):
    """
    Fetch the current logged in user.
    """
    return current_user
