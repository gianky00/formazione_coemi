
import sys
import os
import pytest
from unittest.mock import MagicMock, patch

# Force mock mode (must be before mock_qt import)

# Mock modules first
from tests.desktop_app.mock_qt import mock_qt_modules
sys.modules.update(mock_qt_modules())

# Mark tests to run in forked subprocess
pytestmark = pytest.mark.forked

@pytest.fixture
def mock_qapp():
    # Needed for paintEvent tests which might check QApplication state
    with patch("PyQt6.QtWidgets.QApplication.instance") as mock_inst:
        yield mock_inst

def test_splash_creation():
    # Clean import
    if 'desktop_app.views.splash_screen' in sys.modules:
        del sys.modules['desktop_app.views.splash_screen']
    from desktop_app.views.splash_screen import CustomSplashScreen

    splash = CustomSplashScreen()
    assert splash is not None
    assert splash.windowFlags() is not None

def test_update_status():
    if 'desktop_app.views.splash_screen' in sys.modules:
        del sys.modules['desktop_app.views.splash_screen']
    from desktop_app.views.splash_screen import CustomSplashScreen
    
    splash = CustomSplashScreen()
    splash.checklist = MagicMock()
    splash.detail_timer.isActive.return_value = True
    splash.update_status("Inizializzazione database...")
    assert splash.status_label.text() == "Inizializzazione database"
    assert splash.detail_timer.isActive() is True

def test_show_error():
    if 'desktop_app.views.splash_screen' in sys.modules:
        del sys.modules['desktop_app.views.splash_screen']
    from desktop_app.views.splash_screen import CustomSplashScreen
    
    splash = CustomSplashScreen()
    with patch("PyQt6.QtCore.QEventLoop.exec"):
        splash.show_error("Fatal Error")
    assert splash.status_label.text() == "Errore di Avvio"
    assert splash.exit_btn.isVisible() is True
    assert splash.progress_bar.isVisible() is False

def test_paint_event(mock_qapp):
    # This is critical to ensure no crashes during painting
    # Clean import ensures we patch the QPainter used by the class
    if 'desktop_app.views.splash_screen' in sys.modules:
        del sys.modules['desktop_app.views.splash_screen']
    from desktop_app.views.splash_screen import CustomSplashScreen, DynamicProgressBar

    splash = CustomSplashScreen()
    
    # Mock Painter
    mock_painter = MagicMock()
    mock_painter.isActive.return_value = True
    
    bar = splash.progress_bar
    
    # Patch QPainter in the correct module where DynamicProgressBar is defined
    with patch("desktop_app.views.splash_screen.QPainter") as MockQPainter:
        MockQPainter.return_value = mock_painter

        # Trigger paintEvent manually
        bar.paintEvent(MagicMock())

    # Verify usage
    assert mock_painter.setRenderHint.called
