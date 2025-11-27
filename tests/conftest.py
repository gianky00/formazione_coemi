import pytest
import sys
import os
from fastapi.testclient import TestClient
from contextlib import asynccontextmanager
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from unittest.mock import MagicMock

from app.main import app
from app.db.session import get_db
from app.db.models import Base, User, Corso
from app.api import deps

# In-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    """Dependency override for database sessions in tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@asynccontextmanager
async def no_lifespan(app):
    yield

app.dependency_overrides[get_db] = override_get_db
app.router.lifespan_context = no_lifespan

def override_get_current_user():
    return User(id=1, username="admin", is_admin=True)

def override_check_write_permission():
    pass

app.dependency_overrides[deps.get_current_user] = override_get_current_user
app.dependency_overrides[deps.check_write_permission] = override_check_write_permission

@pytest.fixture(scope="function")
def db_session():
    """
    Creates a clean database with all tables and seeds master courses
    for each test function, dropping them afterwards.
    """
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        # Seed master courses for test convenience
        corsi = [
            {"nome_corso": "ANTINCENDIO", "validita_mesi": 60, "categoria_corso": "ANTINCENDIO"},
            {"nome_corso": "PRIMO SOCCORSO", "validita_mesi": 36, "categoria_corso": "PRIMO SOCCORSO"},
            {"nome_corso": "VISITA MEDICA", "validita_mesi": 0, "categoria_corso": "VISITA MEDICA"},
            {"nome_corso": "General", "validita_mesi": 12, "categoria_corso": "General"},
        ]
        for corso_data in corsi:
            db.add(Corso(**corso_data))
        db.commit()
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def test_client(db_session):
    """Creates a TestClient that uses the clean db_session."""
    with TestClient(app, base_url="http://test") as client:
        yield client

import importlib

@pytest.fixture(scope="function")
def mock_mutable_settings(mocker):
    """
    Mocks MutableSettings and forces a reload of the config module to ensure
    the global 'settings' object is re-instantiated for each test,
    guaranteeing complete test isolation for settings.
    """
    mock_settings_data = {
        "GEMINI_API_KEY": "obf:test_gemini_key",
        "DATABASE_PATH": None,
        "EMAIL_RECIPIENTS_TO": "test@example.com",
        "SMTP_HOST": "smtps.aruba.it",
        "SMTP_PORT": 465,
        "SMTP_USER": "testuser",
        "SMTP_PASSWORD": "testpassword",
        "ALERT_THRESHOLD_DAYS": 60,
        "ALERT_THRESHOLD_DAYS_VISITE": 30,
    }
    mock_mutable_instance = MagicMock()
    mock_mutable_instance.get.side_effect = lambda key, default=None: mock_settings_data.get(key, default)
    mock_mutable_instance.as_dict.return_value = mock_settings_data

    def update_mock(new_settings):
        mock_settings_data.update(new_settings)

    mock_mutable_instance.update.side_effect = update_mock

    mocker.patch("app.core.config.MutableSettings", return_value=mock_mutable_instance)

    # Force a reload of the config module to pick up the new mock
    import app.core.config
    importlib.reload(app.core.config)

    yield mock_mutable_instance
