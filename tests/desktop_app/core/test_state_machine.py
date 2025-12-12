"""
Test per AppStateMachine - CRASH ZERO FASE 5
"""

import pytest
from unittest.mock import MagicMock


@pytest.fixture
def state_machine(qapp, qtbot):
    """Crea una nuova istanza per ogni test."""
    from desktop_app.core.state_machine import AppStateMachine
    
    # Reset singleton per test isolation
    AppStateMachine._instance = None
    sm = AppStateMachine()
    sm.start()
    
    # Process events to ensure state machine is started
    qtbot.wait(50)
    
    yield sm
    
    sm.stop()
    AppStateMachine._instance = None


class TestAppStateMachine:
    """Test per la state machine."""
    
    def test_initial_state(self, state_machine):
        """Test stato iniziale."""
        from desktop_app.core.state_machine import AppState
        
        assert state_machine.current_state() == AppState.INITIALIZING
    
    def test_valid_transition(self, state_machine, qtbot):
        """Test transizione valida."""
        from desktop_app.core.state_machine import AppState, AppTransition
        
        # INITIALIZING → SPLASH
        result = state_machine.trigger(AppTransition.INIT_COMPLETE)
        qtbot.wait(100)  # Processa eventi
        
        assert result is True
        assert state_machine.current_state() == AppState.SPLASH
    
    def test_invalid_transition(self, state_machine, qtbot):
        """Test transizione non valida."""
        from desktop_app.core.state_machine import AppTransition
        
        # Da INITIALIZING non si può andare direttamente a LOGIN_SUCCESS
        result = state_machine.trigger(AppTransition.LOGIN_SUCCESS)
        
        assert result is False
    
    def test_full_login_flow(self, state_machine, qtbot):
        """Test flusso completo di login."""
        from desktop_app.core.state_machine import AppState, AppTransition
        
        transitions = [
            (AppTransition.INIT_COMPLETE, AppState.SPLASH),
            (AppTransition.SPLASH_DONE, AppState.LOGIN),
            (AppTransition.LOGIN_SUBMIT, AppState.AUTHENTICATING),
            (AppTransition.LOGIN_SUCCESS, AppState.TRANSITIONING),
            (AppTransition.TRANSITION_COMPLETE, AppState.MAIN),
        ]
        
        for trans, expected_state in transitions:
            state_machine.trigger(trans)
            qtbot.wait(50)
            assert state_machine.current_state() == expected_state, \
                f"After {trans.name}, expected {expected_state.name}, got {state_machine.current_state().name}"
    
    def test_login_failed_flow(self, state_machine, qtbot):
        """Test flusso login fallito."""
        from desktop_app.core.state_machine import AppState, AppTransition
        
        # Vai a AUTHENTICATING
        state_machine.trigger(AppTransition.INIT_COMPLETE)
        state_machine.trigger(AppTransition.SPLASH_DONE)
        state_machine.trigger(AppTransition.LOGIN_SUBMIT)
        qtbot.wait(100)
        
        assert state_machine.current_state() == AppState.AUTHENTICATING
        
        # Login fallisce
        state_machine.trigger(AppTransition.LOGIN_FAILED)
        qtbot.wait(50)
        
        assert state_machine.current_state() == AppState.LOGIN
    
    def test_logout_flow(self, state_machine, qtbot):
        """Test flusso logout."""
        from desktop_app.core.state_machine import AppState, AppTransition
        
        # Vai a MAIN
        state_machine.trigger(AppTransition.INIT_COMPLETE)
        state_machine.trigger(AppTransition.SPLASH_DONE)
        state_machine.trigger(AppTransition.LOGIN_SUBMIT)
        state_machine.trigger(AppTransition.LOGIN_SUCCESS)
        state_machine.trigger(AppTransition.TRANSITION_COMPLETE)
        qtbot.wait(100)
        
        assert state_machine.current_state() == AppState.MAIN
        
        # Logout
        state_machine.trigger(AppTransition.LOGOUT_REQUEST)
        qtbot.wait(50)
        
        assert state_machine.current_state() == AppState.LOGIN
    
    def test_error_from_any_state(self, state_machine, qtbot):
        """Test che ERROR sia raggiungibile da qualsiasi stato."""
        from desktop_app.core.state_machine import AppState, AppTransition
        
        # Vai a LOGIN
        state_machine.trigger(AppTransition.INIT_COMPLETE)
        state_machine.trigger(AppTransition.SPLASH_DONE)
        qtbot.wait(100)
        
        assert state_machine.current_state() == AppState.LOGIN
        
        # Trigger errore
        result = state_machine.trigger(AppTransition.ERROR_OCCURRED)
        qtbot.wait(50)
        
        assert result is True
        assert state_machine.current_state() == AppState.ERROR
    
    def test_error_recovery(self, state_machine, qtbot):
        """Test recovery da errore."""
        from desktop_app.core.state_machine import AppState, AppTransition
        
        # Vai a ERROR
        state_machine.trigger(AppTransition.INIT_COMPLETE)
        state_machine.trigger(AppTransition.ERROR_OCCURRED)
        qtbot.wait(100)
        
        assert state_machine.current_state() == AppState.ERROR
        
        # Recovery
        state_machine.trigger(AppTransition.ERROR_RECOVERED)
        qtbot.wait(50)
        
        assert state_machine.current_state() == AppState.LOGIN
    
    def test_shutdown_from_any_state(self, state_machine, qtbot):
        """Test che SHUTTING_DOWN sia raggiungibile da qualsiasi stato."""
        from desktop_app.core.state_machine import AppState, AppTransition
        
        # Vai a MAIN
        state_machine.trigger(AppTransition.INIT_COMPLETE)
        state_machine.trigger(AppTransition.SPLASH_DONE)
        state_machine.trigger(AppTransition.LOGIN_SUBMIT)
        state_machine.trigger(AppTransition.LOGIN_SUCCESS)
        state_machine.trigger(AppTransition.TRANSITION_COMPLETE)
        qtbot.wait(100)
        
        assert state_machine.current_state() == AppState.MAIN
        
        # Shutdown
        result = state_machine.trigger(AppTransition.SHUTDOWN_REQUEST)
        qtbot.wait(50)
        
        assert result is True
        assert state_machine.current_state() == AppState.SHUTTING_DOWN
    
    def test_history(self, state_machine, qtbot):
        """Test registrazione storia transizioni."""
        from desktop_app.core.state_machine import AppTransition
        
        state_machine.trigger(AppTransition.INIT_COMPLETE)
        state_machine.trigger(AppTransition.SPLASH_DONE)
        qtbot.wait(100)
        
        history = state_machine.get_history()
        
        assert len(history) >= 2
        assert history[-1]['to'] == 'LOGIN'
    
    def test_state_changed_signal(self, state_machine, qtbot):
        """Test emissione segnale state_changed."""
        from desktop_app.core.state_machine import AppTransition
        
        callback = MagicMock()
        state_machine.state_changed.connect(callback)
        
        state_machine.trigger(AppTransition.INIT_COMPLETE)
        qtbot.wait(100)
        
        assert callback.called
    
    def test_state_entered_signal(self, state_machine, qtbot):
        """Test emissione segnale state_entered."""
        from desktop_app.core.state_machine import AppTransition, AppState
        
        callback = MagicMock()
        state_machine.state_entered.connect(callback)
        
        state_machine.trigger(AppTransition.INIT_COMPLETE)
        qtbot.wait(100)
        
        assert callback.called
        callback.assert_called_with(AppState.SPLASH)
    
    def test_transition_started_signal(self, state_machine, qtbot):
        """Test emissione segnale transition_started."""
        from desktop_app.core.state_machine import AppTransition
        
        callback = MagicMock()
        state_machine.transition_started.connect(callback)
        
        state_machine.trigger(AppTransition.INIT_COMPLETE)
        qtbot.wait(100)
        
        assert callback.called
        callback.assert_called_with(AppTransition.INIT_COMPLETE)
    
    def test_transition_failed_signal(self, state_machine, qtbot):
        """Test emissione segnale transition_failed."""
        from desktop_app.core.state_machine import AppTransition
        
        callback = MagicMock()
        state_machine.transition_failed.connect(callback)
        
        # Prova transizione non valida
        state_machine.trigger(AppTransition.LOGIN_SUCCESS)
        qtbot.wait(100)
        
        assert callback.called
    
    def test_can_transition(self, state_machine, qtbot):
        """Test verifica transizioni valide."""
        from desktop_app.core.state_machine import AppTransition
        
        # Da INITIALIZING
        assert state_machine.can_transition(AppTransition.INIT_COMPLETE) is True
        assert state_machine.can_transition(AppTransition.LOGIN_SUCCESS) is False
        
        # ERROR sempre valido
        assert state_machine.can_transition(AppTransition.ERROR_OCCURRED) is True
        
        # SHUTDOWN sempre valido
        assert state_machine.can_transition(AppTransition.SHUTDOWN_REQUEST) is True
    
    def test_get_valid_transitions(self, state_machine, qtbot):
        """Test ottenimento transizioni valide."""
        from desktop_app.core.state_machine import AppTransition
        
        valid = state_machine.get_valid_transitions()
        
        assert AppTransition.INIT_COMPLETE in valid
        assert AppTransition.ERROR_OCCURRED in valid
        assert AppTransition.SHUTDOWN_REQUEST in valid
        assert AppTransition.LOGIN_SUCCESS not in valid
    
    def test_previous_state(self, state_machine, qtbot):
        """Test recupero stato precedente."""
        from desktop_app.core.state_machine import AppState, AppTransition
        
        # Inizialmente nessuno stato precedente
        state_machine.trigger(AppTransition.INIT_COMPLETE)
        qtbot.wait(100)
        
        assert state_machine.previous_state() == AppState.INITIALIZING
        
        state_machine.trigger(AppTransition.SPLASH_DONE)
        qtbot.wait(50)
        
        assert state_machine.previous_state() == AppState.SPLASH


class TestStateMachineSingleton:
    """Test per singleton pattern."""
    
    def test_singleton(self, qapp, qtbot):
        """Test che get_state_machine ritorna sempre la stessa istanza."""
        from desktop_app.core.state_machine import get_state_machine, AppStateMachine
        
        # Reset singleton
        AppStateMachine._instance = None
        
        sm1 = get_state_machine()
        sm2 = get_state_machine()
        
        assert sm1 is sm2
        
        # Cleanup
        AppStateMachine._instance = None
    
    def test_reset_instance(self, qapp, qtbot):
        """Test reset istanza singleton."""
        from desktop_app.core.state_machine import AppStateMachine
        
        sm1 = AppStateMachine()
        AppStateMachine.reset_instance()
        sm2 = AppStateMachine()
        
        assert sm1 is not sm2
        
        # Cleanup
        AppStateMachine._instance = None


class TestConvenienceMethods:
    """Test per metodi di convenienza."""
    
    def test_trigger_init_complete(self, state_machine, qtbot):
        """Test metodo trigger_init_complete."""
        from desktop_app.core.state_machine import AppState
        
        result = state_machine.trigger_init_complete()
        qtbot.wait(100)
        
        assert result is True
        assert state_machine.current_state() == AppState.SPLASH
    
    def test_trigger_splash_done(self, state_machine, qtbot):
        """Test metodo trigger_splash_done."""
        from desktop_app.core.state_machine import AppState
        
        state_machine.trigger_init_complete()
        qtbot.wait(50)
        
        result = state_machine.trigger_splash_done()
        qtbot.wait(50)
        
        assert result is True
        assert state_machine.current_state() == AppState.LOGIN
    
    def test_trigger_error(self, state_machine, qtbot):
        """Test metodo trigger_error."""
        from desktop_app.core.state_machine import AppState
        
        result = state_machine.trigger_error()
        qtbot.wait(100)
        
        assert result is True
        assert state_machine.current_state() == AppState.ERROR
    
    def test_trigger_shutdown(self, state_machine, qtbot):
        """Test metodo trigger_shutdown."""
        from desktop_app.core.state_machine import AppState
        
        result = state_machine.trigger_shutdown()
        qtbot.wait(100)
        
        assert result is True
        assert state_machine.current_state() == AppState.SHUTTING_DOWN


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
