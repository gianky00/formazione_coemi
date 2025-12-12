"""
Helper per simulare azioni utente.

CRASH ZERO - FASE 7: User Simulation Testing

NOTE: This module requires REAL PyQt6, not mocked Qt.
It should be used only with pytest-qt which provides a real QApplication.
"""

import sys
import time
import importlib
from typing import Optional, Callable

# Force reload of PyQt6 modules to get REAL ones, not mocks
# This is necessary because other test files inject mock Qt into sys.modules
def _get_real_qt():
    """Get real PyQt6 modules, bypassing any mocks."""
    # Remove any mock PyQt6 modules
    mock_keys = [k for k in list(sys.modules.keys()) 
                 if k.startswith('PyQt6') and ('Dummy' in str(sys.modules.get(k)) or 'MagicMock' in str(type(sys.modules.get(k))))]
    for k in mock_keys:
        del sys.modules[k]
    
    # Now import fresh
    QtCore = importlib.import_module('PyQt6.QtCore')
    QtTest = importlib.import_module('PyQt6.QtTest')
    QtWidgets = importlib.import_module('PyQt6.QtWidgets')
    
    return QtCore, QtTest, QtWidgets

# Get real Qt modules
_QtCore, _QtTest, _QtWidgets = _get_real_qt()

# Extract what we need
Qt = _QtCore.Qt
QPoint = _QtCore.QPoint
QTest = _QtTest.QTest
QWidget = _QtWidgets.QWidget
QLineEdit = _QtWidgets.QLineEdit
QPushButton = _QtWidgets.QPushButton
QApplication = _QtWidgets.QApplication

# Store real Qt enum values to avoid issues with mock pollution
_KEY_RETURN = Qt.Key.Key_Return
_KEY_ESCAPE = Qt.Key.Key_Escape
_KEY_TAB = Qt.Key.Key_Tab
_LEFT_BUTTON = Qt.MouseButton.LeftButton
_NO_MODIFIER = Qt.KeyboardModifier.NoModifier
_NO_FOCUS = Qt.FocusPolicy.NoFocus


class UserSimulator:
    """
    Simula interazioni utente realistiche.
    
    Uso:
        sim = UserSimulator(qtbot)
        sim.click(button)
        sim.type_text(input_field, "hello")
        sim.wait_for_animation()
    """
    
    def __init__(self, qtbot):
        self.qtbot = qtbot
        self._action_delay_ms = 20  # Ritardo tra azioni (ridotto per test veloci)
    
    def click(self, widget, pos=None):
        """Simula click su widget."""
        if widget is None or not widget.isVisible():
            return
            
        if pos is None:
            pos = widget.rect().center()
        
        try:
            QTest.mouseClick(widget, _LEFT_BUTTON, pos=pos)
        except RuntimeError:
            # Widget potrebbe essere stato distrutto
            pass
        self._wait_for_events()
    
    def double_click(self, widget, pos=None):
        """Simula doppio click."""
        if widget is None or not widget.isVisible():
            return
            
        if pos is None:
            pos = widget.rect().center()
        
        try:
            QTest.mouseDClick(widget, _LEFT_BUTTON, pos=pos)
        except RuntimeError:
            pass
        self._wait_for_events()
    
    def type_text(self, widget, text: str, clear_first: bool = True):
        """Simula digitazione testo."""
        if widget is None:
            return
            
        try:
            if clear_first:
                widget.clear()
            
            widget.setFocus()
            QTest.keyClicks(widget, text)
        except RuntimeError:
            pass
        self._wait_for_events()
    
    def press_key(self, widget, key, modifier=None):
        """Simula pressione tasto."""
        if widget is None:
            return
        
        if modifier is None:
            modifier = _NO_MODIFIER
            
        try:
            QTest.keyClick(widget, key, modifier)
        except RuntimeError:
            pass
        self._wait_for_events()
    
    def press_enter(self, widget):
        """Simula pressione Enter."""
        self.press_key(widget, _KEY_RETURN)
    
    def press_escape(self, widget):
        """Simula pressione Escape."""
        self.press_key(widget, _KEY_ESCAPE)
    
    def press_tab(self, widget):
        """Simula pressione Tab."""
        self.press_key(widget, _KEY_TAB)
    
    def drag_and_drop(self, source, target):
        """Simula drag and drop."""
        if source is None or target is None:
            return
            
        source_pos = source.rect().center()
        target_pos = target.rect().center()
        
        try:
            QTest.mousePress(source, _LEFT_BUTTON, pos=source_pos)
            QTest.mouseMove(target, pos=target_pos)
            QTest.mouseRelease(target, _LEFT_BUTTON, pos=target_pos)
        except RuntimeError:
            pass
        self._wait_for_events()
    
    def wait_for_visible(self, widget, timeout_ms: int = 5000) -> bool:
        """Attende che widget sia visibile."""
        if widget is None:
            return False
        try:
            self.qtbot.waitUntil(lambda: widget.isVisible(), timeout=timeout_ms)
            return True
        except Exception:
            return False
    
    def wait_for_hidden(self, widget, timeout_ms: int = 5000) -> bool:
        """Attende che widget sia nascosto."""
        if widget is None:
            return True
        try:
            self.qtbot.waitUntil(lambda: not widget.isVisible(), timeout=timeout_ms)
            return True
        except Exception:
            return False
    
    def wait_for_enabled(self, widget, timeout_ms: int = 5000) -> bool:
        """Attende che widget sia abilitato."""
        if widget is None:
            return False
        try:
            self.qtbot.waitUntil(lambda: widget.isEnabled(), timeout=timeout_ms)
            return True
        except Exception:
            return False
    
    def wait_for_animation(self, timeout_ms: int = 1000) -> bool:
        """Attende completamento animazioni."""
        try:
            from desktop_app.core.animation_manager import animation_manager
            
            start = time.time()
            while time.time() - start < timeout_ms / 1000:
                if animation_manager.get_active_count() == 0:
                    return True
                QTest.qWait(50)
            return False
        except ImportError:
            # AnimationManager non disponibile
            QTest.qWait(timeout_ms)
            return True
    
    def wait_for_condition(self, condition: Callable[[], bool], timeout_ms: int = 5000) -> bool:
        """Attende una condizione generica."""
        try:
            self.qtbot.waitUntil(condition, timeout=timeout_ms)
            return True
        except Exception:
            return False
    
    def wait(self, ms: int):
        """Attende un tempo fisso."""
        QTest.qWait(ms)
    
    def process_events(self):
        """Processa eventi Qt pending."""
        app = QApplication.instance()
        if app:
            app.processEvents()
    
    def _wait_for_events(self):
        """Processa eventi Qt e attende."""
        QTest.qWait(self._action_delay_ms)
    
    def find_widget(self, parent, widget_type, name: str = ""):
        """Trova un widget figlio per tipo e nome."""
        if parent is None:
            return None
        
        if name:
            return parent.findChild(widget_type, name)
        else:
            children = parent.findChildren(widget_type)
            return children[0] if children else None
    
    def find_button(self, parent, name: str = ""):
        """Trova un QPushButton."""
        return self.find_widget(parent, QPushButton, name)
    
    def find_input(self, parent, name: str = ""):
        """Trova un QLineEdit."""
        return self.find_widget(parent, QLineEdit, name)
