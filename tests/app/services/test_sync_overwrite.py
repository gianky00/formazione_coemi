from unittest.mock import patch

from app.services.sync_service import get_unique_filename


def test_get_unique_filename_no_conflict():
    with patch("os.path.exists", return_value=False):
        assert get_unique_filename("/tmp", "file.txt") == "file.txt"


def test_get_unique_filename_conflict():
    # Simulate exists for "file.txt", "file_1.txt", but not "file_2.txt"
    def exists_side_effect(path):
        if path.endswith("file.txt"):
            return True
        if path.endswith("file_1.txt"):
            return True
        return False

    with patch("os.path.exists", side_effect=exists_side_effect):
        assert get_unique_filename("/tmp", "file.txt") == "file_2.txt"
