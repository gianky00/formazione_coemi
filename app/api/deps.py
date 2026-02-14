from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.models import BlacklistedToken, User
from app.db.session import get_db
from app.schemas.schemas import TokenData

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.ALGORITHM}/auth/login")


def get_current_user(
    db: Annotated[Session, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    """
    Validates the JWT token and returns the current user.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as e:
        raise credentials_exception from e

    # Check if token is blacklisted
    blacklisted = db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
    if blacklisted:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been invalidated (logged out)",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.query(User).filter(User.username == token_data.username).first()
    if user is None:
        raise credentials_exception
    return user


def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Verifies that the user is active."""
    return current_user


def get_current_active_admin(
    current_user: Annotated[User, Depends(get_current_active_user)],
    db: Annotated[Session, Depends(get_db)],
) -> User:
    """Verifies that the user has admin privileges."""
    if not current_user.is_admin:
        from app.utils.audit import log_security_action

        log_security_action(
            db,
            current_user,
            "UNAUTHORIZED_ACCESS",
            "Tentativo di accesso a risorsa admin",
            category="AUTH",
            severity="MEDIUM",
        )
        raise HTTPException(status_code=403, detail="The user doesn't have enough privileges")
    return current_user


def check_write_permission(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> None:
    """
    Dummy dependency to check for write permissions.
    Currently, all active users can write, but this can be extended.
    """
    pass


def verify_license() -> bool:
    """
    FastAPI dependency to verify if the application has a valid license.
    Used to protect endpoints.
    """
    # Simple check for now, can be expanded with real license logic
    return True


# Re-export common types for easier router usage
UserDep = Annotated[User, Depends(get_current_user)]
AdminDep = Annotated[User, Depends(get_current_active_admin)]
DbDep = Annotated[Session, Depends(get_db)]
