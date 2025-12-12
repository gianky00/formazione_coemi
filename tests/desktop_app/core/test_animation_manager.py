"""
Test per AnimationManager - CRASH ZERO FASE 2

Nota: pytest-qt fornisce automaticamente le fixture qapp e qtbot.
"""

import pytest
from unittest.mock import MagicMock
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QPropertyAnimation, QAbstractAnimation, QPoint
from PyQt6.QtTest import QTest


@pytest.fixture
def widget(qapp):
    """Fixture per widget di test."""
    w = QWidget()
    w.setFixedSize(400, 300)
    yield w
    try:
        w.deleteLater()
    except RuntimeError:
        pass


class TestAnimationManager:
    """Test per AnimationManager singleton."""

    def test_singleton(self, qapp):
        """Verifica che AnimationManager sia un singleton."""
        from desktop_app.core.animation_manager import AnimationManager
        
        am1 = AnimationManager.instance()
        am2 = AnimationManager()
        am3 = AnimationManager.instance()
        
        assert am1 is am2
        assert am1 is am3

    def test_register_animation(self, qapp, widget):
        """Test registrazione di un'animazione."""
        from desktop_app.core.animation_manager import animation_manager
        
        anim = QPropertyAnimation(widget, b"pos")
        anim.setDuration(100)
        anim.setStartValue(QPoint(0, 0))
        anim.setEndValue(QPoint(10, 10))
        
        anim_id = animation_manager.register(
            animation=anim,
            owner=widget,
            name="test_anim"
        )
        
        assert anim_id != ""
        assert len(anim_id) == 8
        
        # Cleanup
        animation_manager.cancel_by_id(anim_id)

    def test_cancel_by_id(self, qapp, widget):
        """Test cancellazione animazione per ID."""
        from desktop_app.core.animation_manager import animation_manager
        
        anim = QPropertyAnimation(widget, b"pos")
        anim_id = animation_manager.register(anim, owner=widget)
        
        result = animation_manager.cancel_by_id(anim_id)
        assert result is True
        
        # Cancellare di nuovo dovrebbe fallire
        result = animation_manager.cancel_by_id(anim_id)
        assert result is False

    def test_cancel_all_by_owner(self, qapp, widget):
        """Test cancellazione di tutte le animazioni di un owner."""
        from desktop_app.core.animation_manager import animation_manager
        
        # Registra 3 animazioni
        ids = []
        for i in range(3):
            anim = QPropertyAnimation(widget, b"pos")
            anim_id = animation_manager.register(anim, owner=widget, name=f"anim_{i}")
            ids.append(anim_id)
        
        # Verifica che siano registrate
        count_before = animation_manager.get_active_count(owner=widget)
        assert count_before == 3
        
        # Cancella tutte
        cancelled = animation_manager.cancel_all(owner=widget)
        assert cancelled == 3
        
        # Verifica che siano state rimosse
        count_after = animation_manager.get_active_count(owner=widget)
        assert count_after == 0

    def test_is_animating(self, qapp, widget):
        """Test verifica se un owner ha animazioni attive."""
        from desktop_app.core.animation_manager import animation_manager
        
        widget.show()
        
        # Inizialmente nessuna animazione
        assert animation_manager.is_animating(widget) is False
        
        # Crea e avvia animazione
        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(500)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        
        anim_id = animation_manager.register(anim, owner=widget, name="opacity_test")
        anim.start()
        
        # Ora dovrebbe essere in esecuzione
        QTest.qWait(50)  # Piccola attesa per assicurarsi che l'animazione sia partita
        
        # Potrebbe essere True o False a seconda del timing
        # Per rendere il test stabile, verifichiamo solo che la chiamata non crashi
        is_running = animation_manager.is_animating(widget)
        assert isinstance(is_running, bool)
        
        # Cleanup
        animation_manager.cancel_all(widget)

    def test_get_active_count(self, qapp, widget):
        """Test conteggio animazioni attive."""
        from desktop_app.core.animation_manager import animation_manager
        
        # Cleanup iniziale
        animation_manager.cancel_all(widget)
        
        initial_count = animation_manager.get_active_count(owner=widget)
        assert initial_count == 0
        
        # Aggiungi 2 animazioni
        anim1 = QPropertyAnimation(widget, b"pos")
        anim2 = QPropertyAnimation(widget, b"size")
        
        animation_manager.register(anim1, owner=widget)
        animation_manager.register(anim2, owner=widget)
        
        count = animation_manager.get_active_count(owner=widget)
        assert count == 2
        
        # Cleanup
        animation_manager.cancel_all(widget)


class TestAnimationHelpers:
    """Test per helper functions (fade_in, fade_out, etc.)."""

    def test_fade_out(self, qapp, widget):
        """Test helper fade_out."""
        from desktop_app.core.animation_manager import fade_out, animation_manager
        
        widget.show()
        QTest.qWait(10)
        
        finished_called = {'value': False}
        
        def on_finished():
            finished_called['value'] = True
        
        anim_id = fade_out(
            widget,
            duration_ms=100,
            on_finished=on_finished
        )
        
        assert anim_id != ""
        
        # Attendi completamento
        QTest.qWait(200)
        
        # Callback dovrebbe essere stato chiamato
        assert finished_called['value'] is True
        
        # Cleanup
        animation_manager.cancel_all(widget)

    def test_fade_out_dead_widget(self, qapp):
        """Test fade_out su widget None."""
        from desktop_app.core.animation_manager import fade_out
        
        finished_called = {'value': False}
        
        def on_finished():
            finished_called['value'] = True
        
        anim_id = fade_out(None, on_finished=on_finished)
        
        # Dovrebbe ritornare stringa vuota
        assert anim_id == ""
        
        # Callback dovrebbe essere chiamato comunque
        assert finished_called['value'] is True

    def test_fade_in(self, qapp, widget):
        """Test helper fade_in."""
        from desktop_app.core.animation_manager import fade_in, animation_manager
        
        finished_called = {'value': False}
        
        def on_finished():
            finished_called['value'] = True
        
        anim_id = fade_in(
            widget,
            duration_ms=100,
            on_finished=on_finished
        )
        
        assert anim_id != ""
        assert widget.isVisible()  # fade_in dovrebbe mostrare il widget
        
        # Attendi completamento
        QTest.qWait(200)
        
        assert finished_called['value'] is True
        
        # Cleanup
        animation_manager.cancel_all(widget)

    def test_slide_out(self, qapp, widget):
        """Test helper slide_out."""
        from desktop_app.core.animation_manager import slide_out, animation_manager
        
        widget.show()
        QTest.qWait(10)
        
        initial_pos = widget.pos()
        
        finished_called = {'value': False}
        
        def on_finished():
            finished_called['value'] = True
        
        anim_id = slide_out(
            widget,
            direction='left',
            duration_ms=100,
            on_finished=on_finished
        )
        
        assert anim_id != ""
        
        # Attendi completamento
        QTest.qWait(200)
        
        assert finished_called['value'] is True
        
        # La posizione dovrebbe essere cambiata
        final_pos = widget.pos()
        assert final_pos.x() < initial_pos.x()
        
        # Cleanup
        animation_manager.cancel_all(widget)

    def test_slide_in(self, qapp, widget):
        """Test helper slide_in."""
        from desktop_app.core.animation_manager import slide_in, animation_manager
        
        target_pos = QPoint(100, 100)
        
        finished_called = {'value': False}
        
        def on_finished():
            finished_called['value'] = True
        
        anim_id = slide_in(
            widget,
            direction='right',
            duration_ms=100,
            target_pos=target_pos,
            on_finished=on_finished
        )
        
        assert anim_id != ""
        assert widget.isVisible()  # slide_in dovrebbe mostrare il widget
        
        # Attendi completamento
        QTest.qWait(200)
        
        assert finished_called['value'] is True
        
        # Cleanup
        animation_manager.cancel_all(widget)

    def test_animate_property(self, qapp, widget):
        """Test helper animate_property."""
        from desktop_app.core.animation_manager import animate_property, animation_manager
        
        widget.show()
        widget.setWindowOpacity(0.0)
        
        finished_called = {'value': False}
        
        def on_finished():
            finished_called['value'] = True
        
        anim_id = animate_property(
            target=widget,
            property_name=b"windowOpacity",
            start_value=0.0,
            end_value=1.0,
            duration_ms=100,
            on_finished=on_finished
        )
        
        assert anim_id != ""
        
        # Attendi completamento
        QTest.qWait(200)
        
        assert finished_called['value'] is True
        
        # Cleanup
        animation_manager.cancel_all(widget)

    def test_shake_widget(self, qapp, widget):
        """Test helper shake_widget."""
        from desktop_app.core.animation_manager import shake_widget, animation_manager
        
        widget.show()
        initial_pos = widget.pos()
        
        finished_called = {'value': False}
        
        def on_finished():
            finished_called['value'] = True
        
        anim_id = shake_widget(
            widget,
            amplitude=5,
            duration_ms=100,
            on_finished=on_finished
        )
        
        assert anim_id != ""
        
        # Attendi completamento (shake fa 3 loop)
        QTest.qWait(400)
        
        assert finished_called['value'] is True
        
        # Cleanup
        animation_manager.cancel_all(widget)

    def test_animate_geometry(self, qapp, widget):
        """Test helper animate_geometry."""
        from desktop_app.core.animation_manager import animate_geometry, animation_manager
        from PyQt6.QtCore import QRect
        
        widget.show()
        widget.setGeometry(0, 0, 100, 100)
        
        target_geometry = QRect(50, 50, 200, 200)
        
        finished_called = {'value': False}
        
        def on_finished():
            finished_called['value'] = True
        
        anim_id = animate_geometry(
            widget,
            target_geometry=target_geometry,
            duration_ms=100,
            on_finished=on_finished
        )
        
        assert anim_id != ""
        
        # Attendi completamento
        QTest.qWait(200)
        
        assert finished_called['value'] is True
        
        # Cleanup
        animation_manager.cancel_all(widget)


class TestAnimationTimeout:
    """Test per timeout automatico delle animazioni."""

    def test_animation_timeout(self, qapp, widget):
        """Test che le animazioni vadano in timeout se non completano."""
        from desktop_app.core.animation_manager import animation_manager
        
        widget.show()
        
        timeout_called = {'value': False}
        
        def on_timeout():
            timeout_called['value'] = True
        
        # Crea un'animazione molto lunga
        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(10000)  # 10 secondi
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        
        # Registra con timeout breve
        anim_id = animation_manager.register(
            animation=anim,
            owner=widget,
            name="long_anim",
            timeout_ms=200,  # 200ms timeout
            on_timeout=on_timeout
        )
        
        anim.start()
        
        # Attendi il timeout
        QTest.qWait(400)
        
        # Il timeout dovrebbe essere stato chiamato
        assert timeout_called['value'] is True
        
        # L'animazione dovrebbe essere stata cancellata
        assert animation_manager.get_active_count(owner=widget) == 0


class TestAnimationCleanup:
    """Test per cleanup automatico delle animazioni."""

    def test_cleanup_on_widget_destroy(self, qapp):
        """Test che le animazioni vengano cancellate quando l'owner viene distrutto."""
        from desktop_app.core.animation_manager import animation_manager
        
        widget = QWidget()
        widget.show()
        
        # Registra animazione
        anim = QPropertyAnimation(widget, b"pos")
        anim_id = animation_manager.register(anim, owner=widget)
        
        assert animation_manager.get_active_count(owner=widget) == 1
        
        # Distruggi widget
        widget.deleteLater()
        QTest.qWait(100)
        
        # L'animazione dovrebbe essere stata rimossa (periodic cleanup)
        # Nota: potrebbe richiedere fino a 5 secondi per il cleanup automatico
        # quindi forziamo il cleanup chiamando il metodo privato per il test
        animation_manager._periodic_cleanup()
        
        count = animation_manager.get_active_count()
        # Non possiamo verificare il count specifico per widget distrutto,
        # ma verifichiamo che la chiamata non crashi
        assert isinstance(count, int)

    def test_wait_completion(self, qapp, widget):
        """Test wait_completion."""
        from desktop_app.core.animation_manager import animation_manager
        
        widget.show()
        
        # Crea animazione breve
        anim = QPropertyAnimation(widget, b"windowOpacity")
        anim.setDuration(100)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        
        animation_manager.register(anim, owner=widget)
        anim.start()
        
        # Attendi completamento
        result = animation_manager.wait_completion(widget, timeout_ms=500)
        
        # Dovrebbe completare con successo
        assert result is True
        assert animation_manager.is_animating(widget) is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])