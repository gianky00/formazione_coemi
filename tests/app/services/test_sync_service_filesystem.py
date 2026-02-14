import os
from unittest.mock import patch

import pytest

from app.services.sync_service import (
    _move_file_safely,
    clean_all_empty_folders,
    get_unique_filename,
    remove_empty_folders,
)


@pytest.fixture
def temp_sync_dir(tmp_path):
    d = tmp_path / "sync_test"
    d.mkdir()
    return str(d)


def test_remove_empty_folders_recursive(temp_sync_dir):
    # Create structure: root/a/b/c
    deep_path = os.path.join(temp_sync_dir, "a", "b", "c")
    os.makedirs(deep_path)

    # Remove c, should recursively remove b and a but stop at root
    remove_empty_folders(deep_path, root_path=temp_sync_dir)

    assert os.path.exists(temp_sync_dir)
    assert not os.path.exists(os.path.join(temp_sync_dir, "a"))


def test_clean_all_empty_folders(temp_sync_dir):
    # Create a mix of empty and non-empty folders
    os.makedirs(os.path.join(temp_sync_dir, "empty1"))
    os.makedirs(os.path.join(temp_sync_dir, "empty2", "nested_empty"))

    full_path = os.path.join(temp_sync_dir, "full")
    os.makedirs(full_path)
    with open(os.path.join(full_path, "file.txt"), "w") as f:
        f.write("test")

    clean_all_empty_folders(temp_sync_dir)

    assert os.path.exists(full_path)
    assert not os.path.exists(os.path.join(temp_sync_dir, "empty1"))
    assert not os.path.exists(os.path.join(temp_sync_dir, "empty2"))


def test_get_unique_filename_logic(temp_sync_dir):
    filename = "cert.pdf"
    # Create first file
    with open(os.path.join(temp_sync_dir, filename), "w") as f:
        f.write("v1")

    # Should suggest cert_1.pdf
    new_name = get_unique_filename(temp_sync_dir, filename)
    assert new_name == "cert_1.pdf"

    # Create cert_1.pdf
    with open(os.path.join(temp_sync_dir, new_name), "w") as f:
        f.write("v2")

    # Should suggest cert_2.pdf
    new_name_2 = get_unique_filename(temp_sync_dir, filename)
    assert new_name_2 == "cert_2.pdf"


def test_move_file_safely_collision(temp_sync_dir):
    # Setup source and destination
    src = os.path.join(temp_sync_dir, "source.pdf")
    with open(src, "w") as f:
        f.write("data")

    dst_dir = os.path.join(temp_sync_dir, "dest")
    os.makedirs(dst_dir)
    dst = os.path.join(dst_dir, "target.pdf")

    # Pre-occupy target
    with open(dst, "w") as f:
        f.write("existing")

    # Move should succeed by renaming to target_1.pdf
    success = _move_file_safely(src, dst, temp_sync_dir)

    assert success is True
    assert not os.path.exists(src)
    assert os.path.exists(dst)  # original still there
    assert os.path.exists(os.path.join(dst_dir, "target_1.pdf"))  # new file created


def test_move_file_safely_same_path(temp_sync_dir):
    path = os.path.join(temp_sync_dir, "file.pdf")
    with open(path, "w") as f:
        f.write("data")

    # Moving to same path should return False (no move needed)
    assert _move_file_safely(path, path, temp_sync_dir) is False


def test_move_file_permission_error(temp_sync_dir):
    src = os.path.join(temp_sync_dir, "locked.pdf")
    with open(src, "w") as f:
        f.write("data")

    dst = os.path.join(temp_sync_dir, "target.pdf")

    # Mock shutil.move to raise PermissionError
    with patch("shutil.move", side_effect=PermissionError("File locked")):
        success = _move_file_safely(src, dst, temp_sync_dir)
        assert success is False
