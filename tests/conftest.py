import pytest
import sys
import os
from fastapi.testclient import TestClient
from contextlib import asynccontextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.db.session import get_db
from app.db.models import Base, User
from app.api import deps

# Set dummy environment variables for tests
os.environ["GEMINI_API_KEY"] = "test_key"
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
os.environ["GCS_BUCKET_NAME"] = "test-bucket"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """
    Dependency override for database sessions in tests.
    """
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

@asynccontextmanager
async def no_lifespan(app):
    """
    Dummy lifespan manager to disable production seeding in tests.
    """
    yield

app.dependency_overrides[get_db] = override_get_db
app.router.lifespan_context = no_lifespan

def override_get_current_user():
    return User(id=1, username="admin", is_admin=True)

def override_check_write_permission():
    """Disable write protection for tests."""
    pass

app.dependency_overrides[deps.get_current_user] = override_get_current_user
app.dependency_overrides[deps.check_write_permission] = override_check_write_permission

@pytest.fixture(scope="function")
def test_client(db_session, mock_mutable_settings):
    """
    Creates a TestClient for the FastAPI application with the correct base URL.
    """
    with TestClient(app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function")
def db_session():
    """
    Creates a clean database session for each test function.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture
def mock_ai_service(mocker):
    """
    Mocks the AI service to return predictable data.
    """
    return mocker.patch("app.api.main.ai_extraction.extract_entities_with_ai")

@pytest.fixture(scope="session")
def admin_token_headers() -> dict:
    """Provides authorization headers for an admin user."""
    return {"Authorization": "Bearer admin-token"}

@pytest.fixture(scope="session")
def user_token_headers() -> dict:
    """Provides authorization headers for a non-admin user."""
    return {"Authorization": "Bearer user-token"}
