import sys
from unittest.mock import MagicMock, patch

# 1. Setup Mocks
from tests.desktop_app import mock_qt
sys.modules["PyQt6"] = mock_qt.mock_modules["PyQt6"]
sys.modules["PyQt6.QtWidgets"] = mock_qt.mock_modules["PyQt6.QtWidgets"]
sys.modules["PyQt6.QtCore"] = mock_qt.mock_modules["PyQt6.QtCore"]
sys.modules["PyQt6.QtGui"] = mock_qt.mock_modules["PyQt6.QtGui"]

from desktop_app.views.splash_screen import CustomSplashScreen

def test_splash_screen_init():
    splash = CustomSplashScreen()
    assert splash.windowOpacity() == 0.0
    assert splash.status_label.text() == ""

def test_update_status():
    splash = CustomSplashScreen()
    
    # Mock checklist
    splash.checklist = MagicMock()
    
    splash.update_status("Inizializzazione database...")
    
    assert splash.status_label.text() == "Inizializzazione database"
    splash.checklist.update_state.assert_called_with("Inizializzazione database")
    
    # Check detail updates
    assert splash.detail_timer.isActive() is True
    assert splash.detail_label.text() == "Inizializzazione SQLite in-memory"

def test_update_status_progress():
    splash = CustomSplashScreen()
    splash.update_status("Loading...", 50)
    assert splash.progress_bar.value() == 50

def test_show_error():
    splash = CustomSplashScreen()
    
    # Mock loop exec to prevent hanging
    with patch("PyQt6.QtCore.QEventLoop.exec"):
        splash.show_error("Fatal Error")
        
    assert splash.status_label.text() == "Errore di Avvio"
    assert splash.exit_btn.isVisible() is True
    assert splash.progress_bar.isVisible() is False

def test_paint_event():
    # This is critical to ensure no crashes during painting
    splash = CustomSplashScreen()
    
    # Mock Painter
    mock_painter = MagicMock()
    
    # We need to simulate paintEvent on the DynamicProgressBar as well, 
    # since that's where the complex drawing is.
    
    bar = splash.progress_bar
    
    with patch("PyQt6.QtGui.QPainter", return_value=mock_painter):
        # Trigger paintEvent manually
        bar.paintEvent(MagicMock())
        
    # Verify painter was used
    # DynamicProgressBar.paintEvent creates QPainter(self)
    # mock_painter should have been instantiated
    assert mock_painter.setRenderHint.called
    assert mock_painter.drawRoundedRect.called

def test_finish():
    splash = CustomSplashScreen()
    mock_window = MagicMock()
    
    # Mock animation start
    splash.finish(mock_window)
    # We just check if animation was created and started
    # Accessing internal attribute if possible or just ensure no crash
    assert hasattr(splash, 'anim_exit_opacity')
