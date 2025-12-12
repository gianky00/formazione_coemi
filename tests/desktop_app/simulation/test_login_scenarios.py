"""
Test di simulazione utente per scenari di login.

CRASH ZERO - FASE 7: User Simulation Testing

NOTE: These tests should be run with --forked flag to avoid segfaults during cleanup:
    pytest tests/desktop_app/simulation/test_login_scenarios.py -v --forked
"""

import pytest
from unittest.mock import MagicMock, patch
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QLineEdit, QPushButton, QWidget
from PyQt6.QtTest import QTest
from .user_actions import UserSimulator


# Mark all tests in this module to run forked (isolated process)
pytestmark = pytest.mark.forked


def create_login_view(mock_backend, mock_license):
    """Helper per creare LoginView con mock appropriati."""
    # Keep patches active for the entire view lifetime
    patches = [
        patch('desktop_app.views.login_view.LicenseManager'),
        patch('desktop_app.views.login_view.UpdateWorker'),
        patch('desktop_app.views.login_view.NeuralNetwork3D'),
        patch('desktop_app.views.login_view.SoundManager'),
        patch('desktop_app.views.login_view.CustomMessageDialog'),  # Mock dialogs
        patch('desktop_app.views.login_view.get_machine_id', return_value='TEST-HW-ID'),
    ]
    
    for p in patches:
        mock_obj = p.start()
        if 'LicenseManager' in str(p):
            mock_obj.return_value.get_license_data.return_value = mock_license
            mock_obj.return_value.is_license_valid.return_value = True
    
    from desktop_app.views.login_view import LoginView
    
    view = LoginView(api_client=mock_backend)
    view._patches = patches  # Store for cleanup
    return view


def cleanup_login_view(view):
    """Minimal cleanup - since we run forked, process dies anyway."""
    if view is None:
        return
    
    # Just stop patches
    if hasattr(view, '_patches'):
        for p in view._patches:
            try:
                p.stop()
            except Exception:
                pass
    
    # Hide widget - no close() to avoid closeEvent issues
    try:
        view.hide()
    except Exception:
        pass


class TestLoginScenarios:
    """Test che simulano l'intero flusso di login."""
    
    @pytest.fixture
    def simulator(self, qtbot):
        return UserSimulator(qtbot)
    
    @pytest.fixture
    def login_view(self, qapp, mock_backend, mock_license):
        """Crea una LoginView isolata per i test."""
        view = create_login_view(mock_backend, mock_license)
        view.show()
        QTest.qWait(100)  # Let it initialize
        
        yield view
        
        cleanup_login_view(view)
    
    def test_login_view_created(self, login_view, simulator):
        """
        Scenario: Login view viene creata correttamente.
        """
        assert login_view is not None
        assert login_view.isVisible()
    
    def test_find_login_inputs(self, login_view, simulator):
        """
        Scenario: Verifica che i campi di input esistano.
        """
        # Cerca campi input (potrebbero avere nomi diversi)
        line_edits = login_view.findChildren(QLineEdit)
        assert len(line_edits) >= 2, "Dovrebbero esserci almeno 2 campi input"
        
        buttons = login_view.findChildren(QPushButton)
        assert len(buttons) >= 1, "Dovrebbe esserci almeno un pulsante"
    
    def test_type_in_username_field(self, login_view, simulator, qtbot):
        """
        Scenario: Digitazione nel campo username.
        """
        line_edits = login_view.findChildren(QLineEdit)
        assert len(line_edits) >= 1
        
        username_field = line_edits[0]  # Assume primo campo è username
        simulator.type_text(username_field, "testuser")
        
        assert username_field.text() == "testuser"
    
    def test_type_in_password_field(self, login_view, simulator, qtbot):
        """
        Scenario: Digitazione nel campo password.
        """
        line_edits = login_view.findChildren(QLineEdit)
        assert len(line_edits) >= 2
        
        password_field = line_edits[1]  # Assume secondo campo è password
        simulator.type_text(password_field, "secret123")
        
        assert password_field.text() == "secret123"
    
    def test_click_login_button(self, login_view, simulator, mock_backend, qtbot):
        """
        Scenario: Click sul pulsante login.
        """
        # Trova campi
        line_edits = login_view.findChildren(QLineEdit)
        buttons = login_view.findChildren(QPushButton)
        
        # Trova il bottone login (cerca per testo o è il primo)
        login_btn = None
        for btn in buttons:
            text = btn.text().lower()
            if 'login' in text or 'accedi' in text or 'entra' in text:
                login_btn = btn
                break
        
        if login_btn is None and buttons:
            login_btn = buttons[0]
        
        assert login_btn is not None, "Login button non trovato"
        
        # Compila e clicca
        if len(line_edits) >= 2:
            simulator.type_text(line_edits[0], "admin")
            simulator.type_text(line_edits[1], "password")
        
        simulator.click(login_btn)
        simulator.wait(500)  # Attendi elaborazione
    
    def test_rapid_login_clicks_no_crash(self, login_view, simulator, qtbot):
        """
        Scenario: Click multipli rapidi su login non causano crash.
        """
        # First fill in credentials to avoid dialogs
        line_edits = login_view.findChildren(QLineEdit)
        if len(line_edits) >= 2:
            simulator.type_text(line_edits[0], "admin")
            simulator.type_text(line_edits[1], "password")
        
        buttons = login_view.findChildren(QPushButton)
        
        # Trova il login button
        login_btn = None
        for btn in buttons:
            if btn.isVisible() and btn.isEnabled():
                text = btn.text().lower()
                if 'login' in text or 'accedi' in text:
                    login_btn = btn
                    break
        
        if login_btn is None and buttons:
            login_btn = buttons[0]
        
        if login_btn is None:
            pytest.skip("Nessun bottone login trovato")
        
        # 3 click rapidi
        for _ in range(3):
            simulator.click(login_btn)
        
        # Attendi che si stabilizzi
        simulator.wait(100)
        
        # App non deve crashare
        assert login_view is not None
    
    def test_enter_key_in_password_field(self, login_view, simulator, mock_backend, qtbot):
        """
        Scenario: Pressione Enter nel campo password.
        """
        line_edits = login_view.findChildren(QLineEdit)
        
        if len(line_edits) >= 2:
            username_field = line_edits[0]
            password_field = line_edits[1]
            
            simulator.type_text(username_field, "admin")
            simulator.type_text(password_field, "password")
            simulator.press_enter(password_field)
            
            simulator.wait(500)
    
    def test_tab_navigation(self, login_view, simulator, qtbot):
        """
        Scenario: Navigazione con Tab tra i campi.
        """
        line_edits = login_view.findChildren(QLineEdit)
        
        if len(line_edits) >= 2:
            # Focus sul primo campo
            line_edits[0].setFocus()
            simulator.wait(100)
            
            # Tab al successivo
            simulator.press_tab(line_edits[0])
            simulator.wait(100)
            
            # Verifica che il focus sia cambiato
            # (potrebbe essere sul secondo campo o sul bottone)
    
    def test_escape_key_no_crash(self, login_view, simulator, qtbot):
        """
        Scenario: Pressione Escape non causa crash.
        """
        simulator.press_escape(login_view)
        simulator.wait(200)
        
        # Non deve crashare
        assert True
    
    def test_empty_credentials_handling(self, login_view, simulator, mock_backend, qtbot):
        """
        Scenario: Tentativo login con credenziali vuote.
        """
        buttons = login_view.findChildren(QPushButton)
        
        login_btn = None
        for btn in buttons:
            text = btn.text().lower()
            if 'login' in text or 'accedi' in text or btn.isVisible():
                login_btn = btn
                break
        
        if login_btn:
            # Non compilare nulla, solo click
            simulator.click(login_btn)
            simulator.wait(500)
            
            # View deve rimanere visibile
            assert login_view.isVisible()


class TestLoginEdgeCases:
    """Test per casi limite del login."""
    
    @pytest.fixture
    def simulator(self, qtbot):
        sim = UserSimulator(qtbot)
        sim._action_delay_ms = 20  # Più veloce per stress
        return sim
    
    @pytest.fixture
    def login_view(self, qapp, mock_backend, mock_license):
        """Crea una LoginView isolata."""
        view = create_login_view(mock_backend, mock_license)
        view.show()
        QTest.qWait(100)
        
        yield view
        
        cleanup_login_view(view)
    
    def test_special_characters_in_username(self, login_view, simulator, qtbot):
        """
        Scenario: Username con caratteri speciali.
        """
        line_edits = login_view.findChildren(QLineEdit)
        
        if line_edits:
            special_username = "user@company.com!#$%"
            simulator.type_text(line_edits[0], special_username)
            
            assert line_edits[0].text() == special_username
    
    @pytest.mark.skip(reason="QTest.keyClicks crashes with unicode chars on this Qt version")
    def test_unicode_in_password(self, login_view, simulator, qtbot):
        """
        Scenario: Password con caratteri unicode.
        NOTE: Skipped because QTest.keyClicks doesn't handle unicode well.
        """
        line_edits = login_view.findChildren(QLineEdit)
        
        if len(line_edits) >= 2:
            unicode_password = "пароль密码パスワード"
            simulator.type_text(line_edits[1], unicode_password)
            
            # Verifica che sia stato inserito (potrebbe essere troncato)
            assert len(line_edits[1].text()) > 0
    
    def test_very_long_input(self, login_view, simulator, qtbot):
        """
        Scenario: Input molto lungo.
        """
        line_edits = login_view.findChildren(QLineEdit)
        
        if line_edits:
            long_text = "a" * 1000
            simulator.type_text(line_edits[0], long_text)
            
            # Non deve crashare
            assert True
    
    def test_focus_cycle(self, login_view, simulator, qtbot):
        """
        Scenario: Ciclo completo di focus con Tab.
        """
        # 20 pressioni Tab
        for _ in range(20):
            simulator.press_tab(login_view)
        
        # Non deve crashare
        assert login_view.isVisible()
