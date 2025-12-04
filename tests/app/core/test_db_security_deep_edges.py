import pytest
from unittest.mock import patch, MagicMock
from app.core.db_security import DBSecurityManager

@pytest.fixture
def manager(tmp_path):
    with patch("app.core.db_security.settings") as mock_settings, \
         patch("app.core.db_security.get_user_data_dir", return_value=tmp_path):
        mock_settings.DATABASE_PATH = str(tmp_path)
        return DBSecurityManager(db_name="test.db")

def test_get_connection_deserialize_missing(manager):
    manager.initial_bytes = b"data"

    # Mock sqlite3.connect to return a conn object that lacks deserialize
    mock_conn = MagicMock()
    del mock_conn.deserialize # Ensure it's gone if it existed
    # Or just ensure it raises AttributeError

    # Wait, MagicMock by default creates attributes on access.
    # We need to make access raise AttributeError.
    # property that raises?

    # Easier: Mock the connect call to return a spec that DOES NOT have deserialize
    # But sqlite3.Connection has it in this env.

    with patch("sqlite3.connect") as mock_connect:
        conn_instance = MagicMock(spec=[]) # Empty spec
        # But we need execute...
        conn_instance.execute = MagicMock()
        mock_connect.return_value = conn_instance

        # When accessing .deserialize, it should fail?
        # MagicMock(spec=[]) raises AttributeError for unknown attrs? Yes.

        with pytest.raises(RuntimeError, match="does not support 'deserialize'"):
            manager.get_connection()

def test_get_connection_deserialize_error(manager):
    manager.initial_bytes = b"data"

    with patch("sqlite3.connect") as mock_connect:
        conn_instance = MagicMock()
        conn_instance.deserialize.side_effect = Exception("Deserialize Fail")
        mock_connect.return_value = conn_instance

        with pytest.raises(RuntimeError, match="Failed to deserialize"):
            manager.get_connection()

def test_load_memory_db_read_error(manager, tmp_path):
    # Ensure db path exists so it tries to read
    manager.db_path = tmp_path / "test.db"
    manager.db_path.write_text("data")

    with patch("builtins.open", side_effect=Exception("Read Error")):
        with pytest.raises(RuntimeError, match="Could not read database"):
            manager.load_memory_db()

def test_safe_write_os_replace_windows_error(manager, tmp_path):
    # Simulate Windows PermissionError on os.replace
    manager.db_path = tmp_path / "test.db"

    with patch("os.name", "nt"), \
         patch("builtins.open", MagicMock()), \
         patch("os.replace", side_effect=[PermissionError("Locked"), None]) as mock_replace, \
         patch("time.sleep"): # Speed up retry

         # The code has a retry decorator on _safe_write?
         # No, the retry decorator wraps the whole function.
         # But inside _safe_write, there is a try/except for os.replace on Windows?
         # Let's check code.
         # "if os.name == 'nt' ... try: os.replace ... except PermissionError: raise"
         # It raises PermissionError, which triggers the retry decorator.
         # So checking retry logic via decorator is hard without delay.

         # We can verify it eventually succeeds if side_effect is [Error, Success].
         manager._safe_write(b"data")
         assert mock_replace.call_count == 2
