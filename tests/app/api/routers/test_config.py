from unittest.mock import patch

def test_move_database_endpoint(test_client, admin_token_headers, tmp_path):
    # Mock db_security.move_database to prevent actual file ops
    with patch("app.api.routers.config.db_security.move_database") as mock_move:
        payload = {"new_path": str(tmp_path)}
        # Note: test_client uses base_url="/api/v1", so we call "/config/move-database"
        response = test_client.post(
            "/config/move-database",
            json=payload,
            headers=admin_token_headers
        )
        assert response.status_code == 200, response.text
        assert response.json() == {"message": "Database spostato con successo."}
        # We need to verify called with Path object
        from pathlib import Path
        mock_move.assert_called_once_with(tmp_path)
