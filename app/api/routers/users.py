from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.db.models import User
from app.db.session import get_db
from app.schemas.schemas import UserCreateSchema, UserSchema, UserUpdateSchema
from app.utils.audit import log_security_action

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserSchema])
def read_users(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_active_admin)],
) -> Any:
    """Ritorna l'elenco di tutti gli utenti (solo admin)."""
    return db.query(User).all()


@router.post("/", response_model=UserSchema)
def create_user(
    *,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_active_admin)],
    user_in: UserCreateSchema,
) -> Any:
    """Crea un nuovo utente (solo admin)."""
    user = db.query(User).filter(User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    if not user_in.password:
        raise HTTPException(
            status_code=400,
            detail="Password is required for new users.",
        )

    new_user = User(
        username=user_in.username,
        hashed_password=security.get_password_hash(user_in.password),
        is_admin=user_in.is_admin,
        account_name=user_in.account_name,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    log_security_action(
        db, current_user, "USER_CREATE", f"Creato utente {new_user.username}", category="ADMIN"
    )
    return new_user


@router.put("/{user_id}", response_model=UserSchema)
def update_user(
    *,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_active_admin)],
    user_id: int,
    user_in: UserUpdateSchema,
) -> Any:
    """Aggiorna un utente esistente (solo admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    if user_in.password:
        user.hashed_password = security.get_password_hash(user_in.password)
    if user_in.is_admin is not None:
        user.is_admin = user_in.is_admin
    if user_in.account_name:
        user.account_name = user_in.account_name

    db.commit()
    db.refresh(user)

    log_security_action(
        db, current_user, "USER_UPDATE", f"Aggiornato utente {user.username}", category="ADMIN"
    )
    return user


@router.delete("/{user_id}", response_model=UserSchema)
def delete_user(
    *,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(deps.get_current_active_admin)],
    user_id: int,
) -> Any:
    """Elimina un utente (solo admin)."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Users cannot delete themselves")

    username = user.username
    db.delete(user)
    db.commit()

    log_security_action(
        db, current_user, "USER_DELETE", f"Eliminato utente {username}", category="ADMIN"
    )
    return user
