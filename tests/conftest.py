import pytest
import sys
import os
from fastapi.testclient import TestClient

# Imposta una chiave API fittizia per i test
os.environ["GEMINI_API_KEY"] = "test_key"
os.environ["GOOGLE_CLOUD_PROJECT"] = "test-project"
os.environ["GCS_BUCKET_NAME"] = "test-bucket"

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.db.session import get_db
from app.db.models import Base

from sqlalchemy.pool import StaticPool

# Configurazione del database di test (in memoria)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Crea le tabelle nel database di test
Base.metadata.create_all(bind=engine)

# Fixture per il database di test
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

from contextlib import asynccontextmanager

@asynccontextmanager
async def no_lifespan(app):
    yield

@pytest.fixture(scope="function")
def test_client(db_session):
    """
    Crea un client di test per l'applicazione FastAPI.
    """
    # Sovrascrivi il lifespan manager per disabilitare il seeding del database
    app.router.lifespan_context = no_lifespan

    with TestClient(app) as client:
        yield client

@pytest.fixture(scope="function")
def db_session():
    """
    Crea una sessione di database pulita per ogni test.
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
    Mock the AI service to return predictable data.
    """
    return mocker.patch("app.api.main.ai_extraction.extract_entities_with_ai")
