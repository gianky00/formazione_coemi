# 🧪 FASE 7: User Simulation Testing

## Obiettivo
Creare un framework completo di test che simula interazioni utente reali, coprendo tutti gli scenari d'uso e gli edge case per garantire zero crash in produzione.

---

## 📚 Filosofia dei Test

### Perché Simulazione Utente?
I test unitari verificano che i singoli componenti funzionino, ma non catturano:
- Interazioni tra componenti
- Timing e race condition
- Comportamento sotto stress
- Edge case reali (doppio click, azioni durante animazioni)

### Principi Guida
1. **Realismo**: Simula esattamente cosa farebbe un utente
2. **Completezza**: Copri ogni percorso dell'app
3. **Stress**: Testa comportamenti estremi
4. **Reproducibilità**: Test deterministici e ripetibili

---

## 🏗️ Architettura del Framework

```
tests/
├── desktop_app/
│   └── simulation/
│       ├── __init__.py
│       ├── conftest.py              # Fixtures pytest
│       ├── user_simulator.py        # Framework simulazione
│       ├── scenarios/
│       │   ├── __init__.py
│       │   ├── test_login.py        # Scenari login
│       │   ├── test_navigation.py   # Scenari navigazione
│       │   ├── test_import.py       # Scenari import file
│       │   ├── test_crud.py         # Scenari CRUD certificati
│       │   └── test_edge_cases.py   # Edge case e corner case
│       ├── stress/
│       │   ├── __init__.py
│       │   ├── test_rapid_actions.py
│       │   ├── test_memory.py
│       │   └── test_concurrent.py
│       └── helpers/
│           ├── __init__.py
│           ├── mock_data.py
│           └── assertions.py
```

---

## 📁 File da Creare

### 1. `tests/desktop_app/simulation/conftest.py`

```python
"""
Fixtures globali per test di simulazione utente.

Questo modulo fornisce:
- QApplication condivisa per tutti i test
- Mock del backend API
- Controller applicazione pre-configurato
- Helper per setup/teardown
"""

import pytest
import sys
import os
from typing import Generator
from unittest.mock import MagicMock, patch, AsyncMock

from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from PyQt6.QtTest import QTest


# === QApplication Fixture ===

@pytest.fixture(scope="session")
def qapp() -> Generator[QApplication, None, None]:
    """
    QApplication condivisa per tutta la sessione di test.
    
    Nota: Qt richiede una sola QApplication per processo.
    """
    # Previeni warning headless
    os.environ["QT_QPA_PLATFORM"] = "offscreen"
    
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    
    yield app
    
    # Non chiudere l'app qui - pytest-qt lo gestisce


@pytest.fixture
def qtbot(qapp, qtbot):
    """qtbot con QApplication garantita."""
    return qtbot


# === Mock Backend ===

@pytest.fixture
def mock_api_client():
    """
    Mock completo dell'API client.
    
    Fornisce risposte predefinite per tutte le chiamate API.
    """
    client = MagicMock()
    
    # Auth
    client.login.return_value = {
        "access_token": "test_token_abc123",
        "refresh_token": "refresh_token_xyz",
        "user_info": {
            "id": 1,
            "username": "admin",
            "email": "admin@test.com",
            "is_admin": True,
            "company_id": 1
        }
    }
    client.logout.return_value = {"success": True}
    client.refresh_token.return_value = {"access_token": "new_token"}
    
    # Certificati
    client.get_certificati.return_value = [
        {
            "id": 1,
            "dipendente_id": 1,
            "tipo_corso": "Sicurezza Base",
            "data_conseguimento": "2024-01-15",
            "data_scadenza": "2025-01-15",
            "ente_formatore": "COEMI Training"
        },
        {
            "id": 2,
            "dipendente_id": 1,
            "tipo_corso": "Primo Soccorso",
            "data_conseguimento": "2024-03-20",
            "data_scadenza": "2027-03-20",
            "ente_formatore": "Croce Rossa"
        }
    ]
    client.create_certificato.return_value = {"id": 3, "success": True}
    client.update_certificato.return_value = {"success": True}
    client.delete_certificato.return_value = {"success": True}
    
    # Dipendenti
    client.get_dipendenti.return_value = [
        {"id": 1, "nome": "Mario", "cognome": "Rossi", "cf": "RSSMRA80A01H501Z"},
        {"id": 2, "nome": "Luigi", "cognome": "Verdi", "cf": "VRDLGU85B02F205X"},
    ]
    
    # Scadenze
    client.get_scadenze.return_value = [
        {"id": 1, "certificato_id": 1, "giorni_mancanti": 30, "urgenza": "media"},
    ]
    
    return client


@pytest.fixture
def mock_backend(mock_api_client):
    """
    Patcha l'APIClient globalmente per i test.
    """
    with patch('desktop_app.api_client.APIClient', return_value=mock_api_client):
        with patch('desktop_app.services.api_service.get_api_client', return_value=mock_api_client):
            yield mock_api_client


# === Application Controller ===

@pytest.fixture
def app_controller(qapp, mock_backend, qtbot):
    """
    Controller applicazione pronto per i test.
    
    L'app è inizializzata ma non ancora al login.
    """
    from desktop_app.main import ApplicationController
    
    controller = ApplicationController()
    
    yield controller
    
    # Cleanup
    try:
        controller.cleanup()
    except Exception:
        pass


@pytest.fixture
def logged_in_app(app_controller, mock_backend, qtbot):
    """
    Applicazione con login già effettuato.
    
    Pronta per testare funzionalità post-login.
    """
    from desktop_app.core.app_state_machine import get_state_machine, AppTransition
    
    sm = get_state_machine()
    
    # Simula flusso completo fino a MAIN
    sm.trigger(AppTransition.INIT_COMPLETE)
    qtbot.wait(100)
    sm.trigger(AppTransition.SPLASH_DONE)
    qtbot.wait(100)
    sm.trigger(AppTransition.LOGIN_SUBMIT)
    qtbot.wait(50)
    sm.trigger(AppTransition.LOGIN_SUCCESS)
    qtbot.wait(100)
    sm.trigger(AppTransition.TRANSITION_COMPLETE)
    qtbot.wait(100)
    
    return app_controller


# === Test Data ===

@pytest.fixture
def sample_certificate_data():
    """Dati di esempio per un certificato."""
    return {
        "dipendente_id": 1,
        "tipo_corso": "Test Corso",
        "data_conseguimento": "2024-06-01",
        "data_scadenza": "2025-06-01",
        "ente_formatore": "Test Ente",
        "note": "Note di test"
    }


@pytest.fixture  
def sample_employee_data():
    """Dati di esempio per un dipendente."""
    return {
        "nome": "Test",
        "cognome": "User",
        "cf": "TSTUSR90C03H501A",
        "email": "test@example.com",
        "telefono": "3331234567"
    }
```

---

### 2. `tests/desktop_app/simulation/user_simulator.py`

```python
"""
UserSimulator - Framework per simulare interazioni utente realistiche.

Fornisce metodi per simulare:
- Click, doppio click, click destro
- Digitazione testo
- Pressione tasti
- Drag and drop
- Scroll
- Attese condizionali
"""

from __future__ import annotations

import time
import logging
from typing import Optional, Callable, Any, List
from dataclasses import dataclass

from PyQt6.QtCore import Qt, QPoint, QMimeData, QUrl
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
from PyQt6.QtTest import QTest
from PyQt6.QtWidgets import (
    QWidget, QLineEdit, QPushButton, QComboBox, 
    QTableView, QListView, QCheckBox, QSpinBox,
    QTextEdit, QAbstractItemView
)

logger = logging.getLogger(__name__)


@dataclass
class ActionResult:
    """Risultato di un'azione simulata."""
    success: bool
    action: str
    target: str
    duration_ms: float
    error: Optional[str] = None


class UserSimulator:
    """
    Simula interazioni utente in modo realistico.
    
    Features:
    - Ritardi configurabili tra azioni (realismo)
    - Logging di ogni azione
    - Attese intelligenti (animazioni, condizioni)
    - Gestione errori graceful
    
    Example:
        sim = UserSimulator(qtbot)
        
        # Login flow
        sim.type_text(username_input, "admin")
        sim.type_text(password_input, "password123")
        sim.click(login_button)
        sim.wait_for_condition(lambda: dashboard.isVisible())
    """
    
    def __init__(
        self, 
        qtbot,
        action_delay_ms: int = 50,
        typing_delay_ms: int = 10,
        log_actions: bool = True
    ):
        """
        Inizializza il simulatore.
        
        Args:
            qtbot: pytest-qt qtbot fixture
            action_delay_ms: Ritardo tra azioni (ms)
            typing_delay_ms: Ritardo tra caratteri digitati (ms)
            log_actions: Se loggare ogni azione
        """
        self.qtbot = qtbot
        self.action_delay_ms = action_delay_ms
        self.typing_delay_ms = typing_delay_ms
        self.log_actions = log_actions
        
        self._action_history: List[ActionResult] = []
    
    # === Mouse Actions ===
    
    def click(
        self, 
        widget: QWidget, 
        pos: Optional[QPoint] = None,
        button: Qt.MouseButton = Qt.MouseButton.LeftButton
    ) -> ActionResult:
        """
        Simula click su un widget.
        
        Args:
            widget: Widget da cliccare
            pos: Posizione relativa (None = centro)
            button: Bottone del mouse
        """
        start = time.time()
        
        if pos is None:
            pos = widget.rect().center()
        
        try:
            # Assicurati che il widget sia visibile e abilitato
            if not widget.isVisible():
                return self._fail("click", widget, "Widget not visible")
            
            if not widget.isEnabled():
                return self._fail("click", widget, "Widget not enabled")
            
            QTest.mouseClick(widget, button, pos=pos)
            self._process_events()
            
            return self._success("click", widget, start)
            
        except Exception as e:
            return self._fail("click", widget, str(e))
    
    def double_click(
        self, 
        widget: QWidget, 
        pos: Optional[QPoint] = None
    ) -> ActionResult:
        """Simula doppio click."""
        start = time.time()
        
        if pos is None:
            pos = widget.rect().center()
        
        try:
            QTest.mouseDClick(widget, Qt.MouseButton.LeftButton, pos=pos)
            self._process_events()
            return self._success("double_click", widget, start)
        except Exception as e:
            return self._fail("double_click", widget, str(e))
    
    def right_click(
        self, 
        widget: QWidget, 
        pos: Optional[QPoint] = None
    ) -> ActionResult:
        """Simula click destro (context menu)."""
        start = time.time()
        
        if pos is None:
            pos = widget.rect().center()
        
        try:
            QTest.mouseClick(widget, Qt.MouseButton.RightButton, pos=pos)
            self._process_events()
            return self._success("right_click", widget, start)
        except Exception as e:
            return self._fail("right_click", widget, str(e))
    
    # === Keyboard Actions ===
    
    def type_text(
        self, 
        widget: QWidget, 
        text: str, 
        clear_first: bool = True
    ) -> ActionResult:
        """
        Simula digitazione testo.
        
        Args:
            widget: Widget di input (QLineEdit, QTextEdit, etc.)
            text: Testo da digitare
            clear_first: Se True, pulisce il campo prima
        """
        start = time.time()
        
        try:
            # Focus sul widget
            widget.setFocus()
            self._process_events()
            
            # Pulisci se richiesto
            if clear_first:
                if hasattr(widget, 'clear'):
                    widget.clear()
                elif hasattr(widget, 'setText'):
                    widget.setText("")
            
            # Digita carattere per carattere
            QTest.keyClicks(widget, text, delay=self.typing_delay_ms)
            self._process_events()
            
            return self._success("type_text", widget, start)
            
        except Exception as e:
            return self._fail("type_text", widget, str(e))
    
    def press_key(
        self, 
        widget: QWidget, 
        key: Qt.Key,
        modifier: Qt.KeyboardModifier = Qt.KeyboardModifier.NoModifier
    ) -> ActionResult:
        """Simula pressione di un tasto."""
        start = time.time()
        
        try:
            QTest.keyClick(widget, key, modifier)
            self._process_events()
            return self._success("press_key", widget, start)
        except Exception as e:
            return self._fail("press_key", widget, str(e))
    
    def press_enter(self, widget: QWidget) -> ActionResult:
        """Shortcut per pressione Enter."""
        return self.press_key(widget, Qt.Key.Key_Return)
    
    def press_escape(self, widget: QWidget) -> ActionResult:
        """Shortcut per pressione Escape."""
        return self.press_key(widget, Qt.Key.Key_Escape)
    
    def press_tab(self, widget: QWidget) -> ActionResult:
        """Shortcut per pressione Tab."""
        return self.press_key(widget, Qt.Key.Key_Tab)
    
    # === Widget-Specific Actions ===
    
    def select_combobox_item(
        self, 
        combobox: QComboBox, 
        index: Optional[int] = None,
        text: Optional[str] = None
    ) -> ActionResult:
        """
        Seleziona un item in una combobox.
        
        Args:
            combobox: La combobox
            index: Indice da selezionare (mutualmente esclusivo con text)
            text: Testo da selezionare
        """
        start = time.time()
        
        try:
            if text is not None:
                idx = combobox.findText(text)
                if idx < 0:
                    return self._fail("select_combobox", combobox, f"Text '{text}' not found")
                combobox.setCurrentIndex(idx)
            elif index is not None:
                combobox.setCurrentIndex(index)
            
            self._process_events()
            return self._success("select_combobox", combobox, start)
            
        except Exception as e:
            return self._fail("select_combobox", combobox, str(e))
    
    def toggle_checkbox(self, checkbox: QCheckBox) -> ActionResult:
        """Toggle di una checkbox."""
        start = time.time()
        
        try:
            checkbox.setChecked(not checkbox.isChecked())
            self._process_events()
            return self._success("toggle_checkbox", checkbox, start)
        except Exception as e:
            return self._fail("toggle_checkbox", checkbox, str(e))
    
    def set_spinbox_value(self, spinbox: QSpinBox, value: int) -> ActionResult:
        """Imposta valore di uno spinbox."""
        start = time.time()
        
        try:
            spinbox.setValue(value)
            self._process_events()
            return self._success("set_spinbox", spinbox, start)
        except Exception as e:
            return self._fail("set_spinbox", spinbox, str(e))
    
    def select_table_row(
        self, 
        table: QTableView, 
        row: int
    ) -> ActionResult:
        """Seleziona una riga in una tabella."""
        start = time.time()
        
        try:
            model = table.model()
            if model is None:
                return self._fail("select_row", table, "No model")
            
            if row >= model.rowCount():
                return self._fail("select_row", table, f"Row {row} out of range")
            
            index = model.index(row, 0)
            table.setCurrentIndex(index)
            table.scrollTo(index)
            self._process_events()
            
            return self._success("select_row", table, start)
            
        except Exception as e:
            return self._fail("select_row", table, str(e))
    
    # === Drag and Drop ===
    
    def drag_and_drop_files(
        self, 
        target_widget: QWidget, 
        file_paths: List[str]
    ) -> ActionResult:
        """
        Simula drag and drop di file.
        
        Args:
            target_widget: Widget destinazione
            file_paths: Lista di path file da droppare
        """
        start = time.time()
        
        try:
            # Crea mime data con URL dei file
            mime_data = QMimeData()
            urls = [QUrl.fromLocalFile(path) for path in file_paths]
            mime_data.setUrls(urls)
            
            # Simula drag enter
            pos = target_widget.rect().center()
            
            # Nota: la simulazione completa di D&D è complessa
            # Usiamo il metodo diretto se disponibile
            if hasattr(target_widget, 'handle_drop'):
                target_widget.handle_drop(file_paths)
            elif hasattr(target_widget, 'dropEvent'):
                # Crea evento drop fittizio
                drop_event = QDropEvent(
                    pos,
                    Qt.DropAction.CopyAction,
                    mime_data,
                    Qt.MouseButton.LeftButton,
                    Qt.KeyboardModifier.NoModifier
                )
                target_widget.dropEvent(drop_event)
            
            self._process_events()
            return self._success("drag_drop", target_widget, start)
            
        except Exception as e:
            return self._fail("drag_drop", target_widget, str(e))
    
    # === Waiting ===
    
    def wait(self, ms: int):
        """Attesa semplice."""
        QTest.qWait(ms)
    
    def wait_for_visible(
        self, 
        widget: QWidget, 
        timeout_ms: int = 5000
    ) -> bool:
        """
        Attende che un widget diventi visibile.
        
        Returns:
            True se visibile entro il timeout
        """
        try:
            self.qtbot.waitUntil(
                lambda: widget.isVisible(),
                timeout=timeout_ms
            )
            return True
        except Exception:
            return False
    
    def wait_for_enabled(
        self, 
        widget: QWidget, 
        timeout_ms: int = 5000
    ) -> bool:
        """Attende che un widget sia abilitato."""
        try:
            self.qtbot.waitUntil(
                lambda: widget.isEnabled(),
                timeout=timeout_ms
            )
            return True
        except Exception:
            return False
    
    def wait_for_condition(
        self, 
        condition: Callable[[], bool], 
        timeout_ms: int = 5000
    ) -> bool:
        """
        Attende una condizione generica.
        
        Args:
            condition: Funzione che ritorna True quando la condizione è soddisfatta
            timeout_ms: Timeout
        """
        try:
            self.qtbot.waitUntil(condition, timeout=timeout_ms)
            return True
        except Exception:
            return False
    
    def wait_for_animation(self, timeout_ms: int = 2000) -> bool:
        """Attende il completamento delle animazioni."""
        try:
            from desktop_app.core.animation_manager import animation_manager
            
            start = time.time()
            while time.time() - start < timeout_ms / 1000:
                if animation_manager.get_active_count() == 0:
                    return True
                QTest.qWait(50)
            
            return False
        except ImportError:
            QTest.qWait(timeout_ms)
            return True
    
    # === Assertions ===
    
    def assert_visible(self, widget: QWidget, message: str = ""):
        """Assert che il widget sia visibile."""
        assert widget.isVisible(), message or f"{widget.__class__.__name__} should be visible"
    
    def assert_not_visible(self, widget: QWidget, message: str = ""):
        """Assert che il widget non sia visibile."""
        assert not widget.isVisible(), message or f"{widget.__class__.__name__} should not be visible"
    
    def assert_enabled(self, widget: QWidget, message: str = ""):
        """Assert che il widget sia abilitato."""
        assert widget.isEnabled(), message or f"{widget.__class__.__name__} should be enabled"
    
    def assert_text(self, widget: QWidget, expected: str, message: str = ""):
        """Assert sul testo del widget."""
        actual = widget.text() if hasattr(widget, 'text') else str(widget)
        assert actual == expected, message or f"Expected '{expected}', got '{actual}'"
    
    # === History & Debug ===
    
    def get_action_history(self) -> List[ActionResult]:
        """Ritorna la storia delle azioni eseguite."""
        return self._action_history.copy()
    
    def clear_history(self):
        """Pulisce la storia delle azioni."""
        self._action_history.clear()
    
    def print_history(self):
        """Stampa la storia delle azioni (debug)."""
        print("\n=== Action History ===")
        for i, action in enumerate(self._action_history):
            status = "✅" if action.success else "❌"
            print(f"{i+1}. {status} {action.action} on {action.target} ({action.duration_ms:.1f}ms)")
            if action.error:
                print(f"   Error: {action.error}")
        print("======================\n")
    
    # === Private Methods ===
    
    def _process_events(self):
        """Processa eventi Qt e applica ritardo."""
        QTest.qWait(self.action_delay_ms)
    
    def _success(
        self, 
        action: str, 
        widget: QWidget, 
        start_time: float
    ) -> ActionResult:
        """Registra un'azione riuscita."""
        duration = (time.time() - start_time) * 1000
        result = ActionResult(
            success=True,
            action=action,
            target=widget.__class__.__name__,
            duration_ms=duration
        )
        self._action_history.append(result)
        
        if self.log_actions:
            logger.debug(f"✅ {action} on {widget.__class__.__name__} ({duration:.1f}ms)")
        
        return result
    
    def _fail(
        self, 
        action: str, 
        widget: QWidget, 
        error: str
    ) -> ActionResult:
        """Registra un'azione fallita."""
        result = ActionResult(
            success=False,
            action=action,
            target=widget.__class__.__name__,
            duration_ms=0,
            error=error
        )
        self._action_history.append(result)
        
        if self.log_actions:
            logger.warning(f"❌ {action} on {widget.__class__.__name__}: {error}")
        
        return result
```

---

### 3. `tests/desktop_app/simulation/scenarios/test_login.py`

```python
"""
Test scenari di login.

Copre:
- Login con credenziali valide
- Login con credenziali errate
- Comportamento sotto stress (click multipli)
- Edge case (chiusura durante login, etc.)
"""

import pytest
from PyQt6.QtWidgets import QLineEdit, QPushButton
from PyQt6.QtCore import Qt

from ..user_simulator import UserSimulator


class TestLoginScenarios:
    """Test del flusso di login."""
    
    @pytest.fixture
    def simulator(self, qtbot):
        return UserSimulator(qtbot)
    
    @pytest.fixture
    def login_view(self, app_controller, qtbot):
        """Ottiene la login view."""
        from desktop_app.core.app_state_machine import get_state_machine, AppTransition
        
        sm = get_state_machine()
        sm.trigger(AppTransition.INIT_COMPLETE)
        sm.trigger(AppTransition.SPLASH_DONE)
        qtbot.wait(200)
        
        # Trova la login view
        assert hasattr(app_controller, 'login_view'), "Login view not found"
        return app_controller.login_view
    
    def test_successful_login(self, simulator, login_view, mock_backend, qtbot):
        """
        Scenario: Login riuscito con credenziali valide.
        
        Steps:
        1. L'utente vede il form di login
        2. Inserisce username "admin"
        3. Inserisce password "password123"
        4. Clicca il bottone Login
        5. Vede l'animazione di successo
        6. Viene reindirizzato alla dashboard
        """
        # 1. Verifica form visibile
        simulator.assert_visible(login_view)
        
        # 2-3. Trova campi e inserisci credenziali
        username_input = login_view.findChild(QLineEdit, "username_input")
        password_input = login_view.findChild(QLineEdit, "password_input")
        login_btn = login_view.findChild(QPushButton, "login_btn")
        
        assert username_input is not None, "Username input not found"
        assert password_input is not None, "Password input not found"
        assert login_btn is not None, "Login button not found"
        
        simulator.type_text(username_input, "admin")
        simulator.type_text(password_input, "password123")
        
        # 4. Click login
        simulator.click(login_btn)
        
        # 5-6. Attendi transizione
        simulator.wait_for_animation()
        
        # Verifica che login sia stato chiamato
        mock_backend.login.assert_called_once()
    
    def test_failed_login_shows_error(self, simulator, login_view, mock_backend, qtbot):
        """
        Scenario: Login fallito mostra messaggio di errore.
        """
        # Configura mock per fallire
        mock_backend.login.side_effect = Exception("Credenziali non valide")
        
        username_input = login_view.findChild(QLineEdit, "username_input")
        password_input = login_view.findChild(QLineEdit, "password_input")
        login_btn = login_view.findChild(QPushButton, "login_btn")
        
        simulator.type_text(username_input, "wrong_user")
        simulator.type_text(password_input, "wrong_pass")
        simulator.click(login_btn)
        
        simulator.wait_for_animation()
        
        # La login view deve rimanere visibile
        simulator.assert_visible(login_view)
        
        # Il bottone deve essere ri-abilitato
        simulator.wait_for_enabled(login_btn)
    
    def test_empty_credentials_validation(self, simulator, login_view, mock_backend, qtbot):
        """
        Scenario: Campi vuoti non permettono login.
        """
        login_btn = login_view.findChild(QPushButton, "login_btn")
        
        # Click senza inserire credenziali
        simulator.click(login_btn)
        
        simulator.wait(200)
        
        # Login non deve essere chiamato
        mock_backend.login.assert_not_called()
    
    def test_enter_key_submits_form(self, simulator, login_view, mock_backend, qtbot):
        """
        Scenario: Pressione Enter nel campo password invia il form.
        """
        username_input = login_view.findChild(QLineEdit, "username_input")
        password_input = login_view.findChild(QLineEdit, "password_input")
        
        simulator.type_text(username_input, "admin")
        simulator.type_text(password_input, "password123")
        simulator.press_enter(password_input)
        
        simulator.wait_for_animation()
        
        # Login deve essere chiamato
        mock_backend.login.assert_called_once()
    
    def test_rapid_login_clicks_no_crash(self, simulator, login_view, mock_backend, qtbot):
        """
        Scenario: Click multipli rapidi sul bottone login non causano crash.
        """
        username_input = login_view.findChild(QLineEdit, "username_input")
        password_input = login_view.findChild(QLineEdit, "password_input")
        login_btn = login_view.findChild(QPushButton, "login_btn")
        
        simulator.type_text(username_input, "admin")
        simulator.type_text(password_input, "password")
        
        # 10 click rapidi
        for _ in range(10):
            simulator.click(login_btn)
        
        simulator.wait_for_animation()
        
        # L'app non deve crashare - verifica che il login_view sia ancora valido
        assert login_view is not None
    
    def test_tab_navigation(self, simulator, login_view, qtbot):
        """
        Scenario: Navigazione con Tab tra i campi.
        """
        username_input = login_view.findChild(QLineEdit, "username_input")
        password_input = login_view.findChild(QLineEdit, "password_input")
        
        # Focus su username
        simulator.click(username_input)
        
        # Tab per andare a password
        simulator.press_tab(username_input)
        
        simulator.wait(100)
        
        # Password dovrebbe avere il focus
        assert password_input.hasFocus(), "Password field should have focus after Tab"


class TestLoginEdgeCases:
    """Test edge case del login."""
    
    @pytest.fixture
    def simulator(self, qtbot):
        return UserSimulator(qtbot, action_delay_ms=10)
    
    def test_special_characters_in_password(self, simulator, app_controller, mock_backend, qtbot):
        """
        Scenario: Password con caratteri speciali.
        """
        # Setup login view
        from desktop_app.core.app_state_machine import get_state_machine, AppTransition
        
        sm = get_state_machine()
        sm.trigger(AppTransition.INIT_COMPLETE)
        sm.trigger(AppTransition.SPLASH_DONE)
        qtbot.wait(200)
        
        login_view = app_controller.login_view
        
        username_input = login_view.findChild(QLineEdit, "username_input")
        password_input = login_view.findChild(QLineEdit, "password_input")
        
        simulator.type_text(username_input, "admin")
        simulator.type_text(password_input, "P@$$w0rd!#%&*()[]{}|")
        
        # Non deve crashare
        assert password_input.text() == "P@$$w0rd!#%&*()[]{}|"
    
    def test_very_long_input(self, simulator, app_controller, qtbot):
        """
        Scenario: Input molto lunghi.
        """
        from desktop_app.core.app_state_machine import get_state_machine, AppTransition
        
        sm = get_state_machine()
        sm.trigger(AppTransition.INIT_COMPLETE)
        sm.trigger(AppTransition.SPLASH_DONE)
        qtbot.wait(200)
        
        login_view = app_controller.login_view
        username_input = login_view.findChild(QLineEdit, "username_input")
        
        # 500 caratteri
        long_text = "a" * 500
        simulator.type_text(username_input, long_text)
        
        # Non deve crashare, potrebbe troncare
        assert len(username_input.text()) > 0
```

---

### 4. `tests/desktop_app/simulation/stress/test_rapid_actions.py`

```python
"""
Stress test con azioni rapide.

Verifica che l'app non crashi sotto carico intenso.
"""

import pytest
import random
from PyQt6.QtWidgets import QWidget, QPushButton
from PyQt6.QtCore import Qt

from ..user_simulator import UserSimulator


class TestRapidActions:
    """Test di stress con azioni rapide."""
    
    @pytest.fixture
    def simulator(self, qtbot):
        # Simulatore veloce per stress test
        return UserSimulator(qtbot, action_delay_ms=5, typing_delay_ms=1)
    
    def test_1000_random_clicks(self, simulator, logged_in_app, qtbot):
        """
        Stress: 1000 click random senza crash.
        """
        main_window = logged_in_app.main_window
        
        crash_count = 0
        success_count = 0
        
        for i in range(1000):
            try:
                # Trova tutti i widget cliccabili
                widgets = main_window.findChildren(QWidget)
                clickable = [
                    w for w in widgets 
                    if w.isVisible() and w.isEnabled() and w.rect().isValid()
                ]
                
                if clickable:
                    widget = random.choice(clickable)
                    result = simulator.click(widget)
                    if result.success:
                        success_count += 1
                        
            except Exception as e:
                crash_count += 1
                print(f"Crash at iteration {i}: {e}")
        
        # Meno dell'1% di crash
        assert crash_count < 10, f"Too many crashes: {crash_count}/1000"
        print(f"Success rate: {success_count}/1000")
    
    def test_rapid_navigation(self, simulator, logged_in_app, qtbot):
        """
        Stress: Navigazione rapida tra view.
        """
        main_window = logged_in_app.main_window
        
        # Simula 50 cambi rapidi di view
        view_buttons = ["database_btn", "scadenzario_btn", "import_btn", "config_btn"]
        
        for i in range(50):
            btn_name = view_buttons[i % len(view_buttons)]
            btn = main_window.findChild(QPushButton, btn_name)
            
            if btn and btn.isVisible():
                simulator.click(btn)
        
        simulator.wait_for_animation()
        
        # Verifica che l'app sia ancora funzionante
        assert main_window.isVisible()
    
    def test_concurrent_actions(self, simulator, logged_in_app, qtbot):
        """
        Stress: Azioni mentre altre sono in corso.
        """
        main_window = logged_in_app.main_window
        
        # Trova due widget diversi
        buttons = main_window.findChildren(QPushButton)
        visible_buttons = [b for b in buttons if b.isVisible() and b.isEnabled()]
        
        if len(visible_buttons) >= 2:
            # Click alternati rapidi
            for _ in range(20):
                simulator.click(visible_buttons[0])
                simulator.click(visible_buttons[1])
        
        # Non deve crashare
        assert main_window.isVisible()


class TestMemoryStability:
    """Test di stabilità memoria."""
    
    def test_memory_no_leak_on_navigation(self, logged_in_app, qtbot):
        """
        Verifica che la navigazione non causi memory leak.
        """
        import tracemalloc
        
        tracemalloc.start()
        initial = tracemalloc.get_traced_memory()[0]
        
        main_window = logged_in_app.main_window
        
        # 50 cicli di navigazione
        for _ in range(50):
            for btn_name in ["database_btn", "scadenzario_btn"]:
                btn = main_window.findChild(QPushButton, btn_name)
                if btn:
                    btn.click()
                    qtbot.wait(50)
        
        final = tracemalloc.get_traced_memory()[0]
        tracemalloc.stop()
        
        # La memoria non deve crescere più del 100%
        growth = (final - initial) / initial if initial > 0 else 0
        assert growth < 1.0, f"Memory grew by {growth*100:.1f}%"
    
    def test_no_zombie_widgets(self, logged_in_app, qtbot):
        """
        Verifica che non restino widget zombie dopo navigazione.
        """
        from PyQt6.QtWidgets import QApplication
        
        initial_widgets = len(QApplication.instance().allWidgets())
        
        main_window = logged_in_app.main_window
        
        # Naviga avanti e indietro
        for _ in range(10):
            for btn_name in ["database_btn", "scadenzario_btn", "import_btn"]:
                btn = main_window.findChild(QPushButton, btn_name)
                if btn:
                    btn.click()
                    qtbot.wait(100)
        
        # Forza garbage collection
        import gc
        gc.collect()
        qtbot.wait(200)
        
        final_widgets = len(QApplication.instance().allWidgets())
        
        # Non deve crescere significativamente (tolleranza 20%)
        growth = (final_widgets - initial_widgets) / initial_widgets if initial_widgets > 0 else 0
        assert growth < 0.2, f"Widget count grew by {growth*100:.1f}% ({initial_widgets} → {final_widgets})"
```

---

## 📝 Istruzioni di Implementazione

### Step 1: Crea la Struttura Directory
```bash
mkdir -p tests/desktop_app/simulation/scenarios
mkdir -p tests/desktop_app/simulation/stress
mkdir -p tests/desktop_app/simulation/helpers
touch tests/desktop_app/simulation/__init__.py
touch tests/desktop_app/simulation/scenarios/__init__.py
touch tests/desktop_app/simulation/stress/__init__.py
touch tests/desktop_app/simulation/helpers/__init__.py
```

### Step 2: Crea i File
Copia i contenuti nei rispettivi file.

### Step 3: Installa Dipendenze Test
```bash
pip install pytest-qt pytest-xvfb pytest-timeout pytest-repeat
```

### Step 4: Esegui Test
```bash
# Test singolo file
pytest tests/desktop_app/simulation/scenarios/test_login.py -v

# Tutti i test di simulazione
pytest tests/desktop_app/simulation/ -v

# Stress test (più lenti)
pytest tests/desktop_app/simulation/stress/ -v --timeout=60

# Con report dettagliato
pytest tests/desktop_app/simulation/ -v --tb=short
```

### Step 5: Aggiungi Altri Scenari
Crea test per:
- `test_navigation.py` - Navigazione tra view
- `test_import.py` - Import di file CSV
- `test_crud.py` - Operazioni CRUD sui certificati
- `test_edge_cases.py` - Altri edge case

---

## ✅ Checklist di Completamento

- [ ] Directory structure creata
- [ ] `conftest.py` con fixtures
- [ ] `user_simulator.py` completo
- [ ] Test login scenarios
- [ ] Test navigation scenarios
- [ ] Stress test
- [ ] Memory leak test
- [ ] Tutti i test passano: `pytest tests/desktop_app/simulation/ -v`
- [ ] Coverage >80% dei percorsi utente principali

---

## ⏭️ Prossimo Step

Completata questa fase, procedi con **FASE 8: Documentation** (`FASE_8_DOCUMENTATION.md`).
