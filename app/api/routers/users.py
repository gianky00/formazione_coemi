import os
from typing import Any, List
from fastapi import APIRouter, Body, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core import security
from app.schemas.schemas import User, UserCreate, UserUpdate
from app.api import deps
from app.db.models import User as UserModel
from app.utils.audit import log_security_action

router = APIRouter()

@router.get("/", response_model=List[User])
def read_users(
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: UserModel = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Retrieve users.
    """
    users = db.query(UserModel).offset(skip).limit(limit).all()
    return users

@router.post("/", response_model=User, dependencies=[Depends(deps.check_write_permission)])
def create_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate,
    current_user: UserModel = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Create new user.
    """
    user = db.query(UserModel).filter(UserModel.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )

    # Force default password to "primoaccesso"
    default_password = os.getenv("DEFAULT_USER_PASSWORD", "primoaccesso") # NOSONAR

    user = UserModel(
        username=user_in.username,
        hashed_password=security.get_password_hash(default_password),
        account_name=user_in.account_name,
        gender=user_in.gender,
        is_admin=user_in.is_admin,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    log_security_action(db, current_user, "USER_CREATE", f"Creato utente: {user.username} (Admin: {user.is_admin})", category="USER_MGMT")

    return user

@router.put("/{user_id}", response_model=User, dependencies=[Depends(deps.check_write_permission)])
def update_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    user_in: UserUpdate,
    current_user: UserModel = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Update a user.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )

    update_data = user_in.model_dump(exclude_unset=True)

    if "username" in update_data and update_data["username"] != user.username:
        existing_user = db.query(UserModel).filter(UserModel.username == update_data["username"]).first()
        if existing_user:
            raise HTTPException(
                status_code=400,
                detail="The user with this username already exists in the system.",
            )

    password_changed = False
    if update_data.get("password"):
        hashed_password = security.get_password_hash(update_data["password"])
        del update_data["password"]
        user.hashed_password = hashed_password
        password_changed = True

    for field, value in update_data.items():
        setattr(user, field, value)

    db.add(user)
    db.commit()
    db.refresh(user)

    if password_changed:
        log_security_action(db, current_user, "PASSWORD_CHANGE", f"Cambiata password per utente: {user.username}", category="USER_MGMT")
    else:
        log_security_action(db, current_user, "USER_UPDATE", f"Aggiornato utente: {user.username}. Campi: {', '.join(update_data.keys())}", category="USER_MGMT")

    return user

@router.delete("/{user_id}", response_model=User, dependencies=[Depends(deps.check_write_permission)])
def delete_user(
    *,
    db: Session = Depends(get_db),
    user_id: int,
    current_user: UserModel = Depends(deps.get_current_active_admin),
) -> Any:
    """
    Delete a user.
    """
    user = db.query(UserModel).filter(UserModel.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    if user.id == current_user.id:
        raise HTTPException(
            status_code=400,
            detail="You cannot delete your own account.",
        )

    username_snapshot = user.username
    db.delete(user)
    db.commit()

    log_security_action(db, current_user, "USER_DELETE", f"Eliminato utente: {username_snapshot}", category="USER_MGMT")

    return user
