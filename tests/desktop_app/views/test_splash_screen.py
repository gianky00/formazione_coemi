
import sys
import pytest
from unittest.mock import MagicMock, patch

# Mock modules first
from tests.desktop_app.mock_qt import mock_qt_modules
sys.modules.update(mock_qt_modules())

from desktop_app.views.splash_screen import CustomSplashScreen, DynamicProgressBar

@pytest.fixture
def mock_qapp():
    # Needed for paintEvent tests which might check QApplication state
    with patch("PyQt6.QtWidgets.QApplication.instance") as mock_inst:
        yield mock_inst

def test_splash_creation():
    splash = CustomSplashScreen()
    assert splash is not None
    assert splash.windowFlags() is not None

def test_update_status():
    splash = CustomSplashScreen()
    
    # Mock checklist
    splash.checklist = MagicMock()
    # Mock timer isActive
    splash.detail_timer.isActive.return_value = True
    
    splash.update_status("Inizializzazione database...")
    
    assert splash.status_label.text() == "Inizializzazione database"
    splash.checklist.update_state.assert_called_with("Inizializzazione database")
    
    # Check detail updates
    assert splash.detail_timer.isActive() is True

def test_show_error():
    splash = CustomSplashScreen()
    
    # Mock loop exec to prevent hanging
    with patch("PyQt6.QtCore.QEventLoop.exec"):
        splash.show_error("Fatal Error")
        
    assert splash.status_label.text() == "Errore di Avvio"
    assert splash.exit_btn.isVisible() is True
    # In MockQt, hide() sets _visible = False
    assert splash.progress_bar.isVisible() is False

def test_paint_event(mock_qapp):
    # This is critical to ensure no crashes during painting
    splash = CustomSplashScreen()
    
    # Mock Painter
    mock_painter = MagicMock()
    mock_painter.isActive.return_value = True
    
    # We need to simulate paintEvent on the DynamicProgressBar as well,
    # since that's where the complex drawing is.
    
    bar = splash.progress_bar
    
    # We must patch QPainter constructor to return our mock
    # because DynamicProgressBar instantiates QPainter(self)
    with patch("desktop_app.views.splash_screen.QPainter", return_value=mock_painter):
        # Trigger paintEvent manually
        bar.paintEvent(MagicMock())

    # Verify painter was used
    # DynamicProgressBar.paintEvent creates QPainter(self)
    # mock_painter should have been instantiated
    assert mock_painter.setRenderHint.called
