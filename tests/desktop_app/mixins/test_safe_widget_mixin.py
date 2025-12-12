"""Test per SafeWidgetMixin."""

import pytest
import sys

pytest.importorskip("PyQt6")

from PyQt6.QtWidgets import QWidget, QPushButton, QLabel, QApplication, QLineEdit
from PyQt6.QtCore import Qt


@pytest.fixture(scope="module")
def qapp():
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def safe_widget_class():
    from desktop_app.mixins.safe_widget_mixin import SafeWidgetMixin
    
    class TestSafeWidget(SafeWidgetMixin, QWidget):
        def __init__(self):
            super().__init__()
            self.button = QPushButton("Click Me")
            self.register_child("button", self.button)
            self.label = QLabel("Status")
            self.register_child("label", self.label)
            self.input = QLineEdit()
            self.register_child("input", self.input)
    
    return TestSafeWidget


@pytest.fixture
def safe_widget(qapp, safe_widget_class):
    widget = safe_widget_class()
    yield widget
    try:
        widget.deleteLater()
    except RuntimeError:
        pass


class TestInit:
    def test_init_creates_safe_children_dict(self, qapp, safe_widget_class):
        widget = safe_widget_class()
        assert hasattr(widget, '_safe_children')
        assert isinstance(widget._safe_children, dict)
        widget.deleteLater()


class TestChildRegistration:
    def test_register_child_adds_to_dict(self, safe_widget):
        new_btn = QPushButton("New")
        safe_widget.register_child("new_btn", new_btn)
        assert "new_btn" in safe_widget._safe_children
        new_btn.deleteLater()
    
    def test_get_child_returns_widget(self, safe_widget):
        btn = safe_widget.get_child("button")
        assert btn is safe_widget.button
    
    def test_has_child(self, safe_widget):
        assert safe_widget.has_child("button") is True
        assert safe_widget.has_child("nonexistent") is False


class TestSafeCall:
    def test_safe_call_executes_callback(self, safe_widget):
        result = safe_widget.safe_call(lambda: 42)
        assert result == 42
    
    def test_safe_call_returns_fallback_when_destroying(self, safe_widget):
        safe_widget._is_destroying = True
        result = safe_widget.safe_call(lambda: 42, fallback=-1)
        assert result == -1


class TestSafeSetMethods:
    def test_safe_set_text(self, safe_widget):
        result = safe_widget.safe_set_text("label", "New Text")
        assert result is True
        assert safe_widget.label.text() == "New Text"
    
    def test_safe_set_enabled(self, safe_widget):
        result = safe_widget.safe_set_enabled("button", False)
        assert result is True
        assert safe_widget.button.isEnabled() is False


class TestStateChecks:
    def test_is_destroying(self, safe_widget):
        assert safe_widget.is_destroying() is False
        safe_widget._is_destroying = True
        assert safe_widget.is_destroying() is True
    
    def test_is_safe_when_alive(self, safe_widget):
        assert safe_widget.is_safe() is True


class TestChildrenStatus:
    def test_children_status(self, safe_widget):
        status = safe_widget.children_status()
        assert isinstance(status, dict)
        assert "button" in status
        assert all(v is True for v in status.values())
    
    def test_alive_children_count(self, safe_widget):
        count = safe_widget.alive_children_count()
        assert count == 3
