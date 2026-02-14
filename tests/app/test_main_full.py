from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app, lifespan, run_maintenance_task


@pytest.fixture(autouse=True)
def reset_app_state():
    """Reset app state before each test."""
    if hasattr(app.state, "startup_error"):
        delattr(app.state, "startup_error")
    yield
    if hasattr(app.state, "startup_error"):
        delattr(app.state, "startup_error")


@pytest.mark.anyio
async def test_lifespan_success():
    # Patch AsyncIOScheduler class
    with patch("app.main.AsyncIOScheduler") as mock_sched_class:
        mock_sched = mock_sched_class.return_value

        # Patch dependencies in app.main
        with (
            patch("app.main.db_security") as mock_sec,
            patch("app.main.seed_database") as mock_seed,
            patch("app.main.genai") as mock_genai,
            patch("app.main.settings") as mock_settings,
        ):
            mock_settings.GEMINI_API_KEY_ANALYSIS = "key"

            async with lifespan(app):
                pass

            mock_sec.load_memory_db.assert_called_once()
            mock_seed.assert_called_once()
            mock_genai.configure.assert_called_once_with(api_key="key")
            mock_sched.start.assert_called_once()
            mock_sched.shutdown.assert_called_once()
            mock_sec.cleanup.assert_called_once()


@pytest.mark.anyio
async def test_lifespan_db_load_failure_fatal():
    with patch("app.main.db_security") as mock_sec:
        mock_sec.load_memory_db.side_effect = PermissionError("Fatal Lock")

        async with lifespan(app):
            pass

        assert getattr(app.state, "startup_error", None) == "Fatal Lock"


@pytest.mark.anyio
async def test_lifespan_db_load_failure_non_fatal():
    with patch("app.main.db_security") as mock_sec:
        mock_sec.load_memory_db.side_effect = Exception("Corrupt")

        with patch("app.main.AsyncIOScheduler"):
            async with lifespan(app):
                pass
            assert getattr(app.state, "startup_error", None) is None


@pytest.mark.anyio
async def test_lifespan_seeding_failure():
    with patch("app.main.db_security"):
        with patch("app.main.seed_database", side_effect=Exception("Seed Fail")):
            with patch("app.main.AsyncIOScheduler"):
                async with lifespan(app):
                    pass
                # Error is logged but doesn't stop startup


def test_startup_error_middleware():
    app.state.startup_error = "Broken"
    client = TestClient(app)
    # Health check is exempt from 503 if we want to see the error
    response = client.get("/api/v1/health")
    assert response.status_code == 503
    assert response.json()["detail"] == "Broken"


def test_maintenance_task():
    with (
        patch("app.main.SessionLocal") as mock_session_cls,
        patch("app.main.organize_expired_files") as mock_org,
    ):
        mock_db = mock_session_cls.return_value
        run_maintenance_task()
        mock_org.assert_called_once_with(mock_db)
        mock_db.close.assert_called_once()


def test_maintenance_task_failure():
    # If SessionLocal fails, it should propagate (or handle if we added handling)
    with patch("app.main.SessionLocal", side_effect=Exception("DB Fail")):
        with pytest.raises(Exception, match="DB Fail"):
            run_maintenance_task()


def test_startup_error_middleware_ok():
    if hasattr(app.state, "startup_error"):
        delattr(app.state, "startup_error")
    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
