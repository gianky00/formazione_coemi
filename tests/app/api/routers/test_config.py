from unittest.mock import patch


def test_move_database_endpoint(test_client, admin_token_headers, tmp_path):
    # Mock db_security.move_database to prevent actual file ops
    with patch("app.api.routers.config.db_security.move_database") as mock_move:
        # Use query parameter as expected by the router
        response = test_client.post(
            f"/system-config/move-database?new_path={tmp_path!s}", headers=admin_token_headers
        )
        assert response.status_code == 200, response.text
        assert response.json() == {"message": "Database spostato con successo."}
        # We need to verify called with Path object
        mock_move.assert_called_once_with(tmp_path)
