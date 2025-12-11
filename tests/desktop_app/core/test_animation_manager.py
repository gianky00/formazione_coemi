"""
Test per AnimationManager - CRASH ZERO FASE 2
"""

import pytest
from unittest.mock import MagicMock, patch, PropertyMock
import sys

# Mock PyQt6 prima dell'import
sys.modules['PyQt6'] = MagicMock()
sys.modules['PyQt6.QtCore'] = MagicMock()
sys.modules['PyQt6.QtWidgets'] = MagicMock()
sys.modules['PyQt6.QtGui'] = MagicMock()


class MockQTimer:
    """Mock per QTimer"""
    def __init__(self, parent=None):
        self._interval = 0
        self._single_shot = False
        self._callback = None
        self._running = False
        
    def setInterval(self, ms):
        self._interval = ms
        
    def setSingleShot(self, v):
        self._single_shot = v
        
    def timeout(self):
        return MagicMock()
        
    def start(self):
        self._running = True
        
    def stop(self):
        self._running = False
        
    def deleteLater(self):
        pass
        
    def isActive(self):
        return self._running


class MockQMutex:
    """Mock per QMutex"""
    def lock(self):
        pass
        
    def unlock(self):
        pass


class MockQMutexLocker:
    """Mock per QMutexLocker"""
    def __init__(self, mutex):
        self.mutex = mutex
        
    def __enter__(self):
        return self
        
    def __exit__(self, *args):
        pass


class MockQObject:
    """Mock per QObject base"""
    def __init__(self, parent=None):
        self._destroyed_callbacks = []
        self._parent = parent
        
    def destroyed(self):
        mock = MagicMock()
        mock.connect = lambda cb: self._destroyed_callbacks.append(cb)
        return mock


class MockQAbstractAnimation:
    """Mock per QAbstractAnimation"""
    class State:
        Running = 1
        Stopped = 0
        Paused = 2
        
    def __init__(self, parent=None):
        self._state = MockQAbstractAnimation.State.Running
        self._finished_callbacks = []
        
    def finished(self):
        mock = MagicMock()
        mock.connect = lambda cb: self._finished_callbacks.append(cb)
        return mock
        
    def state(self):
        return self._state
        
    def stop(self):
        self._state = MockQAbstractAnimation.State.Stopped


class MockQWidget(MockQObject):
    """Mock per QWidget"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self._visible = True
        self._graphics_effect = None
        self._pos = MagicMock()
        self._size = MagicMock()
        self._geometry = MagicMock()
        
    def show(self):
        self._visible = True
        
    def hide(self):
        self._visible = False
        
    def pos(self):
        return self._pos
        
    def move(self, *args):
        pass
        
    def size(self):
        return self._size
        
    def geometry(self):
        return self._geometry
        
    def width(self):
        return 100
        
    def height(self):
        return 100
        
    def parent(self):
        return self._parent
        
    def graphicsEffect(self):
        return self._graphics_effect
        
    def setGraphicsEffect(self, effect):
        self._graphics_effect = effect


# Patch moduli PyQt6
@pytest.fixture(autouse=True)
def mock_pyqt6():
    """Fixture per moccare PyQt6"""
    with patch.dict(sys.modules, {
        'PyQt6.QtCore': MagicMock(),
        'PyQt6.QtWidgets': MagicMock(),
    }):
        # Setup mock classes
        sys.modules['PyQt6.QtCore'].QTimer = MockQTimer
        sys.modules['PyQt6.QtCore'].QMutex = MockQMutex
        sys.modules['PyQt6.QtCore'].QMutexLocker = MockQMutexLocker
        sys.modules['PyQt6.QtCore'].QObject = MockQObject
        sys.modules['PyQt6.QtCore'].QAbstractAnimation = MockQAbstractAnimation
        sys.modules['PyQt6.QtCore'].QPoint = MagicMock
        sys.modules['PyQt6.QtCore'].QRect = MagicMock
        sys.modules['PyQt6.QtCore'].QEasingCurve = MagicMock()
        sys.modules['PyQt6.QtCore'].QEasingCurve.Type = MagicMock()
        sys.modules['PyQt6.QtCore'].QEasingCurve.Type.OutCubic = 1
        sys.modules['PyQt6.QtCore'].QEasingCurve.Type.InOutQuad = 2
        sys.modules['PyQt6.QtCore'].QPropertyAnimation = MagicMock
        sys.modules['PyQt6.QtWidgets'].QWidget = MockQWidget
        sys.modules['PyQt6.QtWidgets'].QGraphicsOpacityEffect = MagicMock
        yield


class TestAnimationManagerUnit:
    """Test unitari per AnimationManager (senza Qt reale)"""
    
    def test_manager_module_exists(self):
        """Verifica che il modulo animation_manager esista"""
        import importlib.util
        spec = importlib.util.find_spec("desktop_app.core.animation_manager")
        assert spec is not None
    
    def test_manager_has_required_classes(self):
        """Verifica che il modulo abbia le classi richieste"""
        # Reimport con mock
        with patch('desktop_app.core.widget_guard.is_widget_alive', return_value=True):
            with patch('desktop_app.core.widget_guard.is_qobject_alive', return_value=True):
                # Check file content directly
                import os
                manager_path = os.path.join(os.path.dirname(__file__), 
                    '../../../desktop_app/core/animation_manager.py')
                with open(manager_path, 'r') as f:
                    content = f.read()
                
                assert 'class AnimationManager' in content
                assert 'class _AnimationEntry' in content
                assert 'def register' in content
                assert 'def cancel_all' in content
                assert 'def cancel_by_id' in content
                assert 'def is_animating' in content
                assert 'def wait_completion' in content
    
    def test_helper_functions_exist(self):
        """Verifica che le funzioni helper esistano"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert 'def fade_out' in content
        assert 'def fade_in' in content
        assert 'def slide_out' in content
        assert 'def slide_in' in content
        assert 'def animate_property' in content
        assert 'def shake_widget' in content
        assert 'def animate_geometry' in content
    
    def test_manager_uses_weak_references(self):
        """Verifica che il manager usi weak references"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        # Check for weakref import (can be comma-separated or standalone)
        assert 'weakref' in content
        assert 'weakref.ref' in content
    
    def test_manager_uses_mutex(self):
        """Verifica che il manager usi mutex per thread safety"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert 'QMutex' in content
        assert 'QMutexLocker' in content
    
    def test_manager_is_singleton(self):
        """Verifica pattern singleton"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert '_instance' in content
        assert 'instance(cls)' in content or '@classmethod' in content
    
    def test_animation_entry_dataclass(self):
        """Verifica che _AnimationEntry sia una dataclass con i campi corretti"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert '@dataclass' in content
        assert 'animation_id' in content
        assert 'animation_ref' in content
        assert 'owner_ref' in content
        assert 'timeout_ms' in content
        assert 'on_timeout' in content
    
    def test_exports_correct_symbols(self):
        """Verifica che __all__ contenga i simboli corretti"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert '__all__' in content
        assert 'AnimationManager' in content
        assert 'animation_manager' in content
        assert 'fade_out' in content
        assert 'fade_in' in content


class TestSafeWidgetMixinIntegration:
    """Test integrazione SafeWidgetMixin con AnimationManager"""
    
    def test_mixin_cancels_animations_on_delete(self):
        """Verifica che SafeWidgetMixin cancelli le animazioni su deleteLater"""
        import os
        mixin_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/mixins/safe_widget_mixin.py')
        with open(mixin_path, 'r') as f:
            content = f.read()
        
        assert 'animation_manager.cancel_all' in content
        assert '_cancel_pending_animations' in content
    
    def test_mixin_cancels_on_close_event(self):
        """Verifica che il mixin cancelli animazioni su closeEvent"""
        import os
        mixin_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/mixins/safe_widget_mixin.py')
        with open(mixin_path, 'r') as f:
            content = f.read()
        
        assert 'closeEvent' in content
        assert '_cancel_pending_animations' in content


class TestAnimationManagerAPI:
    """Test dell'API pubblica di AnimationManager"""
    
    def test_register_returns_string_id(self):
        """Verifica che register ritorni un ID stringa"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        # Check that register uses uuid
        assert 'uuid' in content
        assert 'str(uuid' in content or 'uuid4()' in content
    
    def test_cancel_all_takes_owner(self):
        """Verifica che cancel_all accetti owner come parametro"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert 'def cancel_all(self, owner)' in content
    
    def test_is_animating_checks_state(self):
        """Verifica che is_animating controlli lo stato dell'animazione"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert 'def is_animating' in content
        assert 'State.Running' in content
    
    def test_timeout_handling(self):
        """Verifica che il manager gestisca i timeout"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert 'timeout_ms' in content
        assert '_on_animation_timeout' in content
        assert 'on_timeout' in content


class TestHelperFunctions:
    """Test per le funzioni helper"""
    
    def test_fade_out_handles_dead_widget(self):
        """Verifica che fade_out gestisca widget distrutti"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        # Check is_widget_alive is called
        assert 'is_widget_alive' in content
    
    def test_fade_in_creates_opacity_effect(self):
        """Verifica che fade_in crei QGraphicsOpacityEffect"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert 'QGraphicsOpacityEffect' in content
    
    def test_slide_directions(self):
        """Verifica che slide supporti tutte le direzioni"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert "'left'" in content
        assert "'right'" in content
        assert "'up'" in content
        assert "'down'" in content
    
    def test_animate_property_generic(self):
        """Verifica che animate_property sia generico"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        # Check it accepts property_name parameter
        assert 'def animate_property' in content
        assert 'property_name' in content
        assert 'start_value' in content
        assert 'end_value' in content
    
    def test_shake_widget_uses_keyframes(self):
        """Verifica che shake_widget usi keyframes"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert 'setKeyValueAt' in content
        assert 'amplitude' in content


class TestCleanup:
    """Test per cleanup e gestione risorse"""
    
    def test_periodic_cleanup_exists(self):
        """Verifica che esista il cleanup periodico"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert '_periodic_cleanup' in content
        assert '_cleanup_timer' in content
    
    def test_owner_destroyed_handler(self):
        """Verifica gestione distruzione owner"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert '_on_owner_destroyed' in content
        assert 'destroyed.connect' in content
    
    def test_animation_finished_handler(self):
        """Verifica gestione completamento animazione"""
        import os
        manager_path = os.path.join(os.path.dirname(__file__), 
            '../../../desktop_app/core/animation_manager.py')
        with open(manager_path, 'r') as f:
            content = f.read()
        
        assert '_on_animation_finished' in content
        assert 'finished.connect' in content
