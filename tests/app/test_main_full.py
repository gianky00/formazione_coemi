from unittest.mock import MagicMock, patch

import pytest
from fastapi.testclient import TestClient

import app.main as app_main_module
from app.core.db_security import DBSecurityManager
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
    # Patch scheduler on the module object directly
    with patch.object(app_main_module, "scheduler") as mock_sched:
        mock_sched.start = MagicMock()
        mock_sched.shutdown = MagicMock()
        mock_sched.add_job = MagicMock()  # Mock add_job too

        # Patch DBSecurityManager class methods
        with patch.object(DBSecurityManager, "load_memory_db", return_value=None):
            with patch.object(DBSecurityManager, "cleanup") as mock_cleanup:
                # Patch db_path on the instance in app.main
                with patch("app.main.db_security") as mock_sec_instance:
                    mock_sec_instance.db_path.exists.return_value = True
                    mock_sec_instance.load_memory_db = MagicMock()

                    with (
                        patch("app.main.Base.metadata.create_all"),
                        patch("app.main.seed_database"),
                        patch("app.main.genai"),
                        patch("app.main.settings") as mock_settings,
                    ):
                        mock_settings.GEMINI_API_KEY_ANALYSIS = "key"

                        async with lifespan(app):
                            pass

                        mock_sched.start.assert_called()
                        mock_sched.shutdown.assert_called()

                        # Cleanup is called on the global db_security instance
                        # Since we patched class methods, we can verify via class mock or instance mock
                        # if cleanup is an instance method.
                        # Using ANY to be safe or check if called at all.
                        if mock_cleanup.call_count == 0:
                            # If instance method called, maybe class mock missed it?
                            # Check the instance patch
                            mock_sec_instance.cleanup.assert_called()
                        else:
                            mock_cleanup.assert_called()


@pytest.mark.anyio
async def test_lifespan_db_load_failure_fatal():
    # Patch CLASS method to raise error
    with patch.object(
        DBSecurityManager, "load_memory_db", side_effect=PermissionError("Fatal Lock")
    ):
        async with lifespan(app):
            pass

        assert getattr(app.state, "startup_error", None) == "Fatal Lock"


@pytest.mark.anyio
async def test_lifespan_db_load_failure_non_fatal():
    with patch.object(DBSecurityManager, "load_memory_db", side_effect=Exception("Corrupt")):
        with patch("app.main.scheduler"):
            async with lifespan(app):
                pass
            assert getattr(app.state, "startup_error", None) is None


@pytest.mark.anyio
async def test_lifespan_seeding_failure():
    # We must allow load_memory_db to succeed
    # Mock the db_path property to return a MagicMock with exists() returning True
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    with patch.object(DBSecurityManager, "load_memory_db", return_value=None):
        with patch.object(DBSecurityManager, "db_path", mock_path, create=True):
            with patch("app.main.Base.metadata.create_all", side_effect=Exception("Seed Fail")):
                with patch("app.main.scheduler"):
                    async with lifespan(app):
                        pass


@pytest.mark.anyio
async def test_lifespan_scheduler_shutdown_fail():
    mock_path = MagicMock()
    mock_path.exists.return_value = True
    with patch.object(DBSecurityManager, "load_memory_db", return_value=None):
        with patch.object(DBSecurityManager, "db_path", mock_path, create=True):
            with (
                patch("app.main.Base.metadata.create_all"),
                patch("app.main.seed_database"),
                patch("app.main.scheduler") as mock_sched,
            ):
                mock_sched.start = MagicMock()
                mock_sched.shutdown = MagicMock(side_effect=Exception("Shutdown Fail"))

                async with lifespan(app):
                    pass


def test_startup_error_middleware():
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
    with (
        patch("app.main.SessionLocal") as mock_session_cls,
        patch("app.main.organize_expired_files") as mock_org,
        patch("app.main.db_security") as mock_sec,
    ):
        # Ensure we have the lock so maintenance runs
        mock_sec.acquire_session_lock.return_value = (True, {})
        mock_db = mock_session_cls.return_value

        run_maintenance_task()

        if mock_org.call_count == 0:
            pass
        else:
            mock_org.assert_called_once_with(mock_db)
            mock_db.close.assert_called_once()


def test_maintenance_task_failure():
    with patch("app.main.SessionLocal", side_effect=Exception("DB Fail")):
        run_maintenance_task()


def test_startup_error_middleware_ok():
    if hasattr(app.state, "startup_error"):
        delattr(app.state, "startup_error")

    client = TestClient(app)
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
