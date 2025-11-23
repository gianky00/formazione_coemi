from sqlalchemy.orm import Session
from app.db.models import User
from app.db.seeding import seed_database
from app.core.config import settings
from app.core.security import verify_password, get_password_hash

def test_seeding_updates_admin_password(db_session: Session):
    # 1. Create admin user with WRONG password
    wrong_pass = "wrong_password"
    admin_user = User(
        username=settings.FIRST_RUN_ADMIN_USERNAME,
        hashed_password=get_password_hash(wrong_pass),
        account_name="Old Admin",
        is_admin=True
    )
    db_session.add(admin_user)
    db_session.commit()

    # Verify it is wrong
    db_session.refresh(admin_user)
    assert verify_password(wrong_pass, admin_user.hashed_password)
    assert not verify_password(settings.FIRST_RUN_ADMIN_PASSWORD, admin_user.hashed_password)

    # 2. Run Seeding
    seed_database(db_session)

    # 3. Verify Password is Updated
    db_session.refresh(admin_user)
    assert verify_password(settings.FIRST_RUN_ADMIN_PASSWORD, admin_user.hashed_password)
