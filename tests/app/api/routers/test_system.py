from unittest.mock import MagicMock, patch

from app.api.routers import system

# --- Bug 8: Async Optimize Test ---


def test_optimize_endpoint_async():
    """
    Bug 8: /optimize runs sync_all_files (heavy) in main thread.
    Expectation: Should delegate to background task.
    """
    mock_db = MagicMock()
    mock_bg_tasks = MagicMock()

    # Patch dependencies global because it's imported inside function
    with patch("app.core.db_security.db_security") as mock_security:
        result = system.optimize_system(
            background_tasks=mock_bg_tasks, db=mock_db, current_user=MagicMock()
        )

        # Verify DB optimize called
        mock_security.optimize_database.assert_called_once()

        # Verify Background Task added
        mock_bg_tasks.add_task.assert_called_once()

        # Verify status
        assert result["status"] == "background_task_started"
