"""Test per il modulo widget_guard."""

import pytest
import sys

pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QApplication
from PyQt6.QtCore import Qt


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


class TestIsWidgetAlive:
    def test_alive_widget(self, qapp):
        from desktop_app.core.widget_guard import is_widget_alive
        widget = QWidget()
        assert is_widget_alive(widget) is True
        widget.deleteLater()
    
    def test_none_widget(self, qapp):
        from desktop_app.core.widget_guard import is_widget_alive
        assert is_widget_alive(None) is False


class TestGuardWidgetAccess:
    def test_decorator_allows_alive_widget(self, qapp):
        from desktop_app.core.widget_guard import guard_widget_access
        
        class TestWidget(QWidget):
            @guard_widget_access
            def set_value(self, value):
                self._value = value
                return value
        
        widget = TestWidget()
        result = widget.set_value(42)
        assert result == 42
        assert widget._value == 42
        widget.deleteLater()


class TestWidgetRef:
    def test_get_alive_widget(self, qapp):
        from desktop_app.core.widget_guard import WidgetRef
        btn = QPushButton("Test")
        ref = WidgetRef(btn)
        assert ref.get() is btn
        assert ref.is_alive() is True
        btn.deleteLater()
    
    def test_bool_conversion(self, qapp):
        from desktop_app.core.widget_guard import WidgetRef
        btn = QPushButton("Test")
        ref = WidgetRef(btn)
        assert bool(ref) is True
        btn.deleteLater()


class TestWidgetGuardian:
    def test_register_and_get(self, qapp):
        from desktop_app.core.widget_guard import WidgetGuardian
        guardian = WidgetGuardian()
        btn = QPushButton("Test")
        guardian.register("btn", btn)
        assert guardian.get("btn") is btn
        btn.deleteLater()
    
    def test_all_alive(self, qapp):
        from desktop_app.core.widget_guard import WidgetGuardian
        guardian = WidgetGuardian()
        btn = QPushButton("Test")
        lbl = QLabel("Label")
        guardian.register("btn", btn)
        guardian.register("lbl", lbl)
        assert guardian.all_alive() is True
        assert guardian.alive_count() == 2
        btn.deleteLater()
        lbl.deleteLater()
