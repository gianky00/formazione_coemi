"""
Helper per simulare azioni utente.

CRASH ZERO - FASE 7: User Simulation Testing
"""

from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import QWidget, QLineEdit, QPushButton, QApplication
from typing import Optional, Callable
import time


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
    
    def click(self, widget: QWidget, pos: Optional[QPoint] = None):
        """Simula click su widget."""
        if widget is None or not widget.isVisible():
            return
            
        if pos is None:
            pos = widget.rect().center()
        
        try:
            QTest.mouseClick(widget, Qt.MouseButton.LeftButton, pos=pos)
        except RuntimeError:
            # Widget potrebbe essere stato distrutto
            pass
        self._wait_for_events()
    
    def double_click(self, widget: QWidget, pos: Optional[QPoint] = None):
        """Simula doppio click."""
        if widget is None or not widget.isVisible():
            return
            
        if pos is None:
            pos = widget.rect().center()
        
        try:
            QTest.mouseDClick(widget, Qt.MouseButton.LeftButton, pos=pos)
        except RuntimeError:
            pass
        self._wait_for_events()
    
    def type_text(self, widget: QLineEdit, text: str, clear_first: bool = True):
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
    
    def press_key(self, widget: QWidget, key: Qt.Key, modifier: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier):
        """Simula pressione tasto."""
        if widget is None:
            return
            
        try:
            QTest.keyClick(widget, key, modifier)
        except RuntimeError:
            pass
        self._wait_for_events()
    
    def press_enter(self, widget: QWidget):
        """Simula pressione Enter."""
        self.press_key(widget, Qt.Key.Key_Return)
    
    def press_escape(self, widget: QWidget):
        """Simula pressione Escape."""
        self.press_key(widget, Qt.Key.Key_Escape)
    
    def press_tab(self, widget: QWidget):
        """Simula pressione Tab."""
        self.press_key(widget, Qt.Key.Key_Tab)
    
    def drag_and_drop(self, source: QWidget, target: QWidget):
        """Simula drag and drop."""
        if source is None or target is None:
            return
            
        source_pos = source.rect().center()
        target_pos = target.rect().center()
        
        try:
            QTest.mousePress(source, Qt.MouseButton.LeftButton, pos=source_pos)
            QTest.mouseMove(target, pos=target_pos)
            QTest.mouseRelease(target, Qt.MouseButton.LeftButton, pos=target_pos)
        except RuntimeError:
            pass
        self._wait_for_events()
    
    def wait_for_visible(self, widget: QWidget, timeout_ms: int = 5000) -> bool:
        """Attende che widget sia visibile."""
        if widget is None:
            return False
        try:
            self.qtbot.waitUntil(lambda: widget.isVisible(), timeout=timeout_ms)
            return True
        except Exception:
            return False
    
    def wait_for_hidden(self, widget: QWidget, timeout_ms: int = 5000) -> bool:
        """Attende che widget sia nascosto."""
        if widget is None:
            return True
        try:
            self.qtbot.waitUntil(lambda: not widget.isVisible(), timeout=timeout_ms)
            return True
        except Exception:
            return False
    
    def wait_for_enabled(self, widget: QWidget, timeout_ms: int = 5000) -> bool:
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
    
    def find_widget(self, parent: QWidget, widget_type, name: str = "") -> Optional[QWidget]:
        """Trova un widget figlio per tipo e nome."""
        if parent is None:
            return None
        
        if name:
            return parent.findChild(widget_type, name)
        else:
            children = parent.findChildren(widget_type)
            return children[0] if children else None
    
    def find_button(self, parent: QWidget, name: str = "") -> Optional[QPushButton]:
        """Trova un QPushButton."""
        return self.find_widget(parent, QPushButton, name)
    
    def find_input(self, parent: QWidget, name: str = "") -> Optional[QLineEdit]:
        """Trova un QLineEdit."""
        return self.find_widget(parent, QLineEdit, name)
