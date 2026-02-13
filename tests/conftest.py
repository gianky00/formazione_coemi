import asyncio
import os
import sys
from unittest.mock import MagicMock

# --- GLOBAL KILL SWITCH (MUST BE BEFORE ANY APP IMPORTS) ---
# Prevent external services (Sentry, PostHog, WMI) from starting background threads or making network calls.
# This prevents "Access Violation" and "I/O operation on closed file" crashes during teardown.

# 1. Mock 'wmi' to prevent OS calls (Hardware ID)
mock_wmi = MagicMock()
mock_wmi.WMI.return_value = MagicMock()
sys.modules["wmi"] = mock_wmi

# 2. Mock 'posthog' to prevent analytics threads
mock_ph = MagicMock()
mock_ph.capture.return_value = None
mock_ph.flush.return_value = None
sys.modules["posthog"] = mock_ph

# 3. Mock 'sentry_sdk' and its integrations to prevent error tracking threads
mock_sentry = MagicMock()
mock_sentry.init.return_value = None
mock_sentry.is_initialized.return_value = False
mock_sentry.capture_exception.return_value = None
mock_sentry.capture_message.return_value = None
sys.modules["sentry_sdk"] = mock_sentry
sys.modules["sentry_sdk.integrations"] = MagicMock()
sys.modules["sentry_sdk.integrations.fastapi"] = MagicMock()
sys.modules["sentry_sdk.integrations.starlette"] = MagicMock()

# 4. Mock 'wandb' (if present)
sys.modules["wandb"] = MagicMock()

# 5. Disable 'atexit' handlers
# This prevents launcher.py's 'track_exit' from running after pytest closes the loop.
import atexit

atexit.register = MagicMock()

# --- APP IMPORTS (Now safe to import) ---
from contextlib import asynccontextmanager

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import sessionmaker

from app.api import deps
from app.core.config import settings
from app.core.db_security import db_security
from app.db.models import Base, User
from app.db.session import engine, get_db
from app.main import app

# Env setup
os.environ["GEMINI_API_KEY"] = "test_key"
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
os.environ["GCS_BUCKET_NAME"] = "test-bucket"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


@pytest.fixture(scope="session")
def event_loop():
    """
    Creates a session-scoped event loop.
    This prevents 'Event loop is closed' errors when fixtures with different scopes
    try to use the same loop or when async teardown happens.
    """
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()

    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_dirs(tmp_path_factory):
    """Creates a temporary directory for data storage."""
    d = tmp_path_factory.mktemp("data")
    return d


@pytest.fixture(scope="session", autouse=True)
def mock_settings(test_dirs):
    """
    Force settings to use the temporary directory.
    We patch the underlying mutable data dictionary.
    """
    # Mock data to match what SettingsManager expects
    mock_data = {
        "DATABASE_PATH": str(test_dirs),
        "GEMINI_API_KEY_ANALYSIS": "obf:test_key_123",  # Obfuscated format
        "GEMINI_API_KEY_CHAT": "obf:test_chat_key_123",
        "SMTP_HOST": "localhost",
        "SMTP_PORT": 1025,
        "SMTP_USER": "test@example.com",
        "SMTP_PASSWORD": "test",
        "EMAIL_RECIPIENTS_TO": "test@example.com",
        "EMAIL_RECIPIENTS_CC": "",
        "ALERT_THRESHOLD_DAYS": 60,
        "ALERT_THRESHOLD_DAYS_VISITE": 30,
        "FIRST_RUN_ADMIN_USERNAME": "admin",
        "FIRST_RUN_ADMIN_PASSWORD": "prova",
    }

    # Patch the mutable settings object
    settings.mutable._data = mock_data
    return mock_data


@pytest.fixture(scope="session", autouse=True)
def setup_security_manager(test_dirs):
    """
    Configures the DBSecurityManager to work in the test environment.
    Mocks encryption and locking but keeps the core logic intact.
    """
    # 1. Redirect paths
    db_security.data_dir = test_dirs
    db_security.db_path = test_dirs / "database_documenti.db"
    db_security.lock_path = test_dirs / ".database_documenti.db.lock"

    # 2. Mock Encryption (Fernet) - Passthrough
    mock_fernet = MagicMock()
    mock_fernet.encrypt.side_effect = lambda x: x
    mock_fernet.decrypt.side_effect = lambda x: x
    db_security.fernet = mock_fernet

    # 3. Mock LockManager - Default to Success
    db_security.lock_manager = MagicMock()
    db_security.lock_manager.acquire.return_value = (True, {"user": "test_runner"})
    db_security.lock_manager.update_heartbeat.return_value = True
    db_security.lock_manager.release.return_value = True

    return db_security


@pytest.fixture(scope="function")
def db_session(setup_security_manager):
    """
    Provides a clean database session for each test.
    Resets DBSecurityManager state and Engine pool.
    """
    # 1. Reset DBSecurityManager State
    db_security.active_connection = None
    db_security.initial_bytes = None
    db_security.is_read_only = False

    # 2. Clean up disk (mocked disk)
    if db_security.db_path.exists():
        os.remove(db_security.db_path)

    # 3. Dispose Engine (Clear StaticPool)
    engine.dispose()

    # 4. Initialize Connection (This triggers load_memory_db, which will find no file and start empty)
    # We call get_connection explicitly to ensure the global 'active_connection' is set
    connection = db_security.get_connection()

    # 5. Create Tables
    Base.metadata.create_all(bind=engine)

    # 6. Create Session
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()

    try:
        yield session
    finally:
        session.close()
        # Cleanup
        if db_security.active_connection:
            db_security.active_connection.close()
        db_security.active_connection = None


@pytest.fixture(scope="function")
def test_client(db_session):
    """
    FastAPI TestClient with overridden DB dependency.
    """

    def override_get_db():
        yield db_session

    def override_get_current_user():
        return User(id=1, username="admin", is_admin=True, hashed_password="hashed_secret")

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[deps.check_write_permission] = lambda: (
        None
    )  # Always allow write in basic tests
    app.dependency_overrides[deps.verify_license] = lambda: True  # Bypass license check in tests
    app.dependency_overrides[deps.get_current_user] = override_get_current_user

    # Disable lifespan to prevent startup errors from invalid config/env
    @asynccontextmanager
    async def no_lifespan(app):
        yield

    app.router.lifespan_context = no_lifespan

    # Set base_url to include the API prefix so tests using relative paths work
    with TestClient(app, base_url="http://testserver/api/v1") as client:
        yield client

    app.dependency_overrides = {}


@pytest.fixture
def mock_ai_service(mocker):
    """
    Mock the AI extraction service.
    """
    return mocker.patch("app.services.ai_extraction.extract_entities_with_ai")


@pytest.fixture(scope="session")
def admin_token_headers():
    return {"Authorization": "Bearer admin-token"}


@pytest.fixture(scope="session")
def user_token_headers():
    return {"Authorization": "Bearer user-token"}


@pytest.fixture
def override_user_auth(db_session):
    """
    Fixture to simulate an authenticated user.
    """
    # Create the user in the DB
    user = User(username="admin", is_admin=True, hashed_password="hashed_secret")
    db_session.add(user)
    db_session.commit()

    def override():
        return user

    app.dependency_overrides[deps.get_current_user] = override
    yield
    # Clean up handled by db_session rollback/close


@pytest.fixture
def anyio_backend():
    return "asyncio"
