import pytest
from unittest.mock import MagicMock, patch, AsyncMock
from fastapi.testclient import TestClient
from app.main import lifespan, app, run_maintenance_task
import asyncio

@pytest.fixture(autouse=True)
def reset_app_state():
    """Reset app state before each test."""
    app.state.startup_error = None
    yield
    app.state.startup_error = None

@pytest.mark.anyio
async def test_lifespan_success():
    # Mock everything to ensure clean startup
    with patch("app.main.db_security") as mock_sec, \
         patch("app.main.Base.metadata.create_all"), \
         patch("app.main.seed_database"), \
         patch("app.main.genai"), \
         patch("app.main.scheduler") as mock_sched, \
         patch("app.main.settings") as mock_settings:

        mock_settings.GEMINI_API_KEY_ANALYSIS = "key"

        # Run lifespan
        async with lifespan(app):
            pass

        mock_sec.load_memory_db.assert_called_once()
        mock_sched.start.assert_called_once()
        # shutdown is called on exit
        mock_sched.shutdown.assert_called_once()
        mock_sec.cleanup.assert_called_once()

@pytest.mark.anyio
async def test_lifespan_db_load_failure_fatal():
    with patch("app.main.db_security") as mock_sec:
        mock_sec.load_memory_db.side_effect = PermissionError("Fatal Lock")

        async with lifespan(app):
            pass

        assert app.state.startup_error == "Fatal Lock"

@pytest.mark.anyio
async def test_lifespan_db_load_failure_non_fatal():
    with patch("app.main.db_security") as mock_sec, \
         patch("app.main.scheduler"):
        mock_sec.load_memory_db.side_effect = Exception("Corrupt")

        async with lifespan(app):
            pass

        # Should not set startup_error (allows UI to load)
        assert getattr(app.state, "startup_error", None) is None

@pytest.mark.anyio
async def test_lifespan_seeding_failure():
    with patch("app.main.db_security"), \
         patch("app.main.Base.metadata.create_all", side_effect=Exception("Seed Fail")), \
         patch("app.main.scheduler"):

        # Should catch and continue
        async with lifespan(app):
            pass

@pytest.mark.anyio
async def test_lifespan_scheduler_shutdown_fail():
    with patch("app.main.db_security"), \
         patch("app.main.Base.metadata.create_all"), \
         patch("app.main.seed_database"), \
         patch("app.main.scheduler") as mock_sched:

        mock_sched.shutdown.side_effect = Exception("Shutdown Fail")

        async with lifespan(app):
            pass
        # Should not raise

def test_startup_error_middleware():
    # Simulate error state
    app.state.startup_error = "Broken"
    client = TestClient(app)

    response = client.get("/api/v1/health")
    assert response.status_code == 503
    assert response.json()["detail"] == "Broken"

def test_health_check_with_error():
    app.state.startup_error = "Broken"
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 503
    assert response.json()["detail"] == "Broken"

def test_maintenance_task():
    with patch("app.main.SessionLocal") as mock_session, \
         patch("app.main.organize_expired_files") as mock_org:

        run_maintenance_task()
        mock_org.assert_called()
        mock_session.return_value.close.assert_called()

def test_maintenance_task_failure():
    with patch("app.main.SessionLocal", side_effect=Exception("DB Fail")):
        run_maintenance_task() # Should print error but not crash

def test_startup_error_middleware_ok():
    app.state.startup_error = None
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
