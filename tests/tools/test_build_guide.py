from unittest.mock import patch

from tools.build_guide import build_guide


@patch("tools.build_guide.subprocess.run")
@patch("tools.build_guide.shutil.which")
@patch("tools.build_guide.os.path.exists")
def test_build_guide_success(mock_exists, mock_which, mock_run):
    # Mock npm exists
    mock_which.return_value = "/usr/bin/npm"

    # Mock directory existence (guide_dir and index.html)
    # We need side_effect because we check multiple paths
    def exists_side_effect(path):
        if "guide_frontend" in path and "dist" not in path:
            return True  # guide dir exists
        if "index.html" in path:
            return True  # build result exists
        return False

    mock_exists.side_effect = exists_side_effect

    result = build_guide()

    assert result is True
    assert mock_run.call_count == 2  # install and build


@patch("tools.build_guide.shutil.which")
def test_build_guide_no_npm(mock_which):
    mock_which.return_value = None
    result = build_guide()
    assert result is False


@patch("tools.build_guide.subprocess.run")
@patch("tools.build_guide.shutil.which")
@patch("tools.build_guide.os.path.exists")
def test_build_guide_subprocess_error(mock_exists, mock_which, mock_run):
    mock_which.return_value = "npm"
    mock_exists.return_value = True

    import subprocess

    mock_run.side_effect = subprocess.CalledProcessError(1, "cmd")

    result = build_guide()
    assert result is False
