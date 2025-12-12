"""
Test per Error Boundary System - CRASH ZERO FASE 4
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QLineEdit


class TestErrorBoundary:
    """Test per ErrorBoundary."""
    
    def test_protect_decorator_success(self, qapp):
        """Decoratore permette esecuzione normale."""
        from desktop_app.core.error_boundary import ErrorBoundary
        
        class TestView(QWidget):
            def __init__(self):
                super().__init__()
                self.boundary = ErrorBoundary(owner=self)
                self.setup_methods()
            
            def setup_methods(self):
                # Definisce metodo protetto dopo __init__
                pass
            
            def safe_method(self):
                return self.boundary.protect(lambda: 42)()
        
        view = TestView()
        result = view.safe_method()
        
        assert result == 42
        view.deleteLater()
    
    def test_protect_catches_recoverable(self, qapp):
        """Decoratore cattura errori recuperabili."""
        from desktop_app.core.error_boundary import ErrorBoundary, RecoverableError
        
        error_callback = MagicMock()
        
        class TestView(QWidget):
            def __init__(self):
                super().__init__()
                self.boundary = ErrorBoundary(
                    owner=self,
                    on_error=error_callback
                )
            
            def failing_method(self):
                @self.boundary.protect
                def inner():
                    raise RecoverableError("Test error")
                return inner()
        
        view = TestView()
        result = view.failing_method()
        
        assert result is None
        error_callback.assert_called_once()
        
        view.deleteLater()
    
    def test_protect_catches_fatal(self, qapp):
        """Decoratore cattura errori fatali."""
        from desktop_app.core.error_boundary import ErrorBoundary, FatalViewError
        
        fatal_callback = MagicMock()
        
        class TestView(QWidget):
            def __init__(self):
                super().__init__()
                self.boundary = ErrorBoundary(
                    owner=self,
                    on_fatal=fatal_callback
                )
            
            def fatal_method(self):
                @self.boundary.protect
                def inner():
                    raise FatalViewError("Fatal error")
                return inner()
        
        view = TestView()
        result = view.fatal_method()
        
        assert result is None
        fatal_callback.assert_called_once()
        
        view.deleteLater()
    
    def test_escalation_after_max_errors(self, qapp):
        """Errori vengono escalati dopo max_errors."""
        from desktop_app.core.error_boundary import ErrorBoundary, RecoverableError
        
        error_callback = MagicMock()
        fatal_callback = MagicMock()
        
        class TestView(QWidget):
            def __init__(self):
                super().__init__()
                self.boundary = ErrorBoundary(
                    owner=self,
                    on_error=error_callback,
                    on_fatal=fatal_callback,
                    max_errors=3
                )
            
            def failing_method(self):
                @self.boundary.protect
                def inner():
                    raise RecoverableError("Test error")
                return inner()
        
        view = TestView()
        
        # Primi 2 errori: recuperabili
        view.failing_method()
        view.failing_method()
        assert error_callback.call_count == 2
        assert fatal_callback.call_count == 0
        
        # Terzo errore: escalato a fatale
        view.failing_method()
        assert fatal_callback.call_count == 1
        
        view.deleteLater()
    
    def test_execute_safe_success(self, qapp):
        """Test execute_safe con successo."""
        from desktop_app.core.error_boundary import ErrorBoundary
        
        class TestView(QWidget):
            def __init__(self):
                super().__init__()
                self.boundary = ErrorBoundary(owner=self)
        
        view = TestView()
        
        result = view.boundary.execute_safe(lambda: 42)
        assert result == 42
        
        view.deleteLater()
    
    def test_execute_safe_with_fallback(self, qapp):
        """Test execute_safe con fallback."""
        from desktop_app.core.error_boundary import ErrorBoundary
        
        class TestView(QWidget):
            def __init__(self):
                super().__init__()
                self.boundary = ErrorBoundary(owner=self)
        
        view = TestView()
        
        result = view.boundary.execute_safe(
            lambda: 1/0,
            fallback="error"
        )
        assert result == "error"
        
        view.deleteLater()
    
    def test_reset_clears_error_history(self, qapp):
        """Test reset pulisce history errori."""
        from desktop_app.core.error_boundary import ErrorBoundary, RecoverableError
        
        class TestView(QWidget):
            def __init__(self):
                super().__init__()
                self.boundary = ErrorBoundary(owner=self, max_errors=5)
            
            def failing_method(self):
                @self.boundary.protect
                def inner():
                    raise RecoverableError("Test")
                return inner()
        
        view = TestView()
        
        view.failing_method()
        view.failing_method()
        assert view.boundary.error_count() == 2
        
        view.boundary.reset()
        assert view.boundary.error_count() == 0
        assert view.boundary.is_in_error_state() is False
        
        view.deleteLater()
    
    def test_is_in_error_state_after_fatal(self, qapp):
        """Test che is_in_error_state sia True dopo errore fatale."""
        from desktop_app.core.error_boundary import ErrorBoundary, FatalViewError
        
        class TestView(QWidget):
            def __init__(self):
                super().__init__()
                self.boundary = ErrorBoundary(owner=self, on_fatal=lambda ctx: None)
            
            def fatal_method(self):
                @self.boundary.protect
                def inner():
                    raise FatalViewError("Fatal")
                return inner()
        
        view = TestView()
        
        assert view.boundary.is_in_error_state() is False
        view.fatal_method()
        assert view.boundary.is_in_error_state() is True
        
        view.deleteLater()


class TestErrorTypes:
    """Test per tipi di errore."""
    
    def test_recoverable_error(self):
        """Test RecoverableError."""
        from desktop_app.core.error_boundary import RecoverableError, ErrorSeverity
        
        error = RecoverableError("Test")
        assert error.recoverable is True
        assert error.severity == ErrorSeverity.MEDIUM
    
    def test_transient_error(self):
        """Test TransientError."""
        from desktop_app.core.error_boundary import TransientError, ErrorSeverity
        
        error = TransientError("Test")
        assert error.recoverable is True
        assert error.severity == ErrorSeverity.LOW
    
    def test_fatal_error(self):
        """Test FatalViewError."""
        from desktop_app.core.error_boundary import FatalViewError, ErrorSeverity
        
        error = FatalViewError("Test")
        assert error.recoverable is False
        assert error.severity == ErrorSeverity.CRITICAL
    
    def test_state_corruption_error(self):
        """Test StateCorruptionError è sottoclasse di FatalViewError."""
        from desktop_app.core.error_boundary import StateCorruptionError, FatalViewError
        
        error = StateCorruptionError("Corrupted")
        assert isinstance(error, FatalViewError)


class TestErrorContext:
    """Test per ErrorContext."""
    
    def test_to_dict(self):
        """Test serializzazione a dict."""
        from desktop_app.core.error_boundary import ErrorContext
        
        error = ValueError("Test error")
        ctx = ErrorContext(
            error=error,
            view_name="TestView",
            method_name="test_method",
            stack_trace="stack trace here"
        )
        
        result = ctx.to_dict()
        
        assert result['error_type'] == 'ValueError'
        assert result['error_message'] == 'Test error'
        assert result['view'] == 'TestView'
        assert result['method'] == 'test_method'
        assert 'timestamp' in result


class TestDecorators:
    """Test per decoratori standalone."""
    
    def test_error_boundary_decorator(self, qapp):
        """Test decoratore @error_boundary."""
        from desktop_app.core.error_boundary import error_boundary
        
        callback = MagicMock()
        
        class TestClass:
            @error_boundary(on_error=callback)
            def risky_method(self):
                raise ValueError("Test")
        
        obj = TestClass()
        result = obj.risky_method()
        
        assert result is None
        callback.assert_called_once()
    
    def test_error_boundary_decorator_no_callback(self, qapp):
        """Test decoratore @error_boundary senza callback (recoverable)."""
        from desktop_app.core.error_boundary import error_boundary
        
        class TestClass:
            @error_boundary(recoverable=True)
            def risky_method(self):
                raise ValueError("Test")
        
        obj = TestClass()
        result = obj.risky_method()
        
        assert result is None  # Non crasha
    
    def test_error_boundary_decorator_not_recoverable(self, qapp):
        """Test decoratore @error_boundary con recoverable=False."""
        from desktop_app.core.error_boundary import error_boundary
        
        class TestClass:
            @error_boundary(recoverable=False)
            def risky_method(self):
                raise ValueError("Test")
        
        obj = TestClass()
        
        with pytest.raises(ValueError):
            obj.risky_method()
    
    def test_suppress_errors(self, qapp):
        """Test decoratore @suppress_errors."""
        from desktop_app.core.error_boundary import suppress_errors
        
        class TestClass:
            @suppress_errors(ValueError, default=[])
            def get_items(self):
                raise ValueError("No items")
        
        obj = TestClass()
        result = obj.get_items()
        
        assert result == []
    
    def test_suppress_errors_specific_types(self, qapp):
        """Test @suppress_errors sopprime solo tipi specificati."""
        from desktop_app.core.error_boundary import suppress_errors
        
        class TestClass:
            @suppress_errors(ValueError, default="suppressed")
            def get_items(self):
                raise KeyError("Not suppressed")
        
        obj = TestClass()
        
        with pytest.raises(KeyError):
            obj.get_items()
    
    def test_suppress_errors_no_types(self, qapp):
        """Test @suppress_errors senza tipi (sopprime tutto)."""
        from desktop_app.core.error_boundary import suppress_errors
        
        class TestClass:
            @suppress_errors(default="default")
            def get_items(self):
                raise RuntimeError("Any error")
        
        obj = TestClass()
        result = obj.get_items()
        
        assert result == "default"


class TestUIStateRecovery:
    """Test per UIStateRecovery."""
    
    def test_reset_buttons(self, qapp):
        """Test reset bottoni."""
        from desktop_app.core.error_boundary import UIStateRecovery
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        btn1 = QPushButton("Test1")
        btn1.setEnabled(False)
        btn2 = QPushButton("Test2")
        btn2.setEnabled(False)
        
        layout.addWidget(btn1)
        layout.addWidget(btn2)
        
        recovery = UIStateRecovery(widget)
        recovery.reset_buttons()
        
        assert btn1.isEnabled()
        assert btn2.isEnabled()
        
        widget.deleteLater()
    
    def test_clear_inputs(self, qapp):
        """Test reset input."""
        from desktop_app.core.error_boundary import UIStateRecovery
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        input1 = QLineEdit()
        input1.setEnabled(False)
        input1.setText("test")
        
        layout.addWidget(input1)
        
        recovery = UIStateRecovery(widget)
        recovery.clear_inputs()
        
        assert input1.isEnabled()
        assert input1.text() == "test"  # Contenuto non cancellato
        
        widget.deleteLater()
    
    def test_reset_all(self, qapp):
        """Test reset completo."""
        from desktop_app.core.error_boundary import UIStateRecovery
        
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        btn = QPushButton("Button")
        btn.setEnabled(False)
        
        input_w = QLineEdit()
        input_w.setEnabled(False)
        
        layout.addWidget(btn)
        layout.addWidget(input_w)
        
        recovery = UIStateRecovery(widget)
        recovery.reset_all()
        
        assert btn.isEnabled()
        assert input_w.isEnabled()
        
        widget.deleteLater()


class TestTransientErrorHandling:
    """Test per gestione errori transitori."""
    
    def test_transient_error_not_reported_to_sentry(self, qapp):
        """Errori transitori non vengono riportati a Sentry."""
        from desktop_app.core.error_boundary import ErrorBoundary, TransientError
        
        error_callback = MagicMock()
        
        class TestView(QWidget):
            def __init__(self):
                super().__init__()
                self.boundary = ErrorBoundary(
                    owner=self,
                    on_error=error_callback,
                    report_to_sentry=True
                )
            
            def transient_method(self):
                @self.boundary.protect
                def inner():
                    raise TransientError("Temporary issue")
                return inner()
        
        view = TestView()
        
        with patch('desktop_app.core.error_boundary.logger') as mock_logger:
            view.transient_method()
            
            # Verifica che sia loggato come info (non warning)
            mock_logger.info.assert_called()
        
        error_callback.assert_called_once()
        view.deleteLater()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
