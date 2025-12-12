# Contribuire a Intelleo

Grazie per l'interesse nel contribuire a Intelleo. Per garantire la stabilità e la sicurezza di questo software critico, tutti i contributi devono aderire ai seguenti protocolli.

## 1. Principi Architetturali

### Zero-Trust Local
*   **Assunto**: L'utente ha accesso fisico alla macchina e può tentare di manipolare file o memoria.
*   **Regola**: MAI salvare dati sensibili (password, token, PII) in chiaro su disco.
*   **Implementazione**: Usa sempre `DBSecurityManager` (Encryption-at-Rest) e `app.core.string_obfuscation` per secret statici.

### In-Memory First
*   Il database vive su disco solo come blob cifrato (AES-128).
*   A runtime, deve essere caricato esclusivamente in RAM (`:memory:`).

## 2. Standard di Codice

### Lingua
*   **Codice**: INGLESE (Variabili, Funzioni, Commenti Interni).
*   **UI (Label, Dialoghi)**: ITALIANO.
*   **Documentazione**: ITALIANO (per Business Logic), INGLESE (per Build/Agent).

### Terminologia Business (UI)
| Codice (Db/Backend) | UI (Frontend/Utente) |
| :--- | :--- |
| `Dipendente` | **DIPENDENTE** |
| `Certificato` | **DOCUMENTO** |
| `Corso` | **TIPO DOCUMENTO** |
| `Data Rilascio` | **DATA EMISSIONE** |

### Style Guide
*   **Python**: PEP 8 standard. Max line length 120.
*   **Naming Convention**:
    *   Classi: `PascalCase` (`LicenseManager`)
    *   Funzioni/Variabili: `snake_case` (`calculate_expiry`)
    *   Costanti: `UPPER_CASE` (`DEFAULT_TIMEOUT`)

## 3. Workflow Git

### Branching Model
*   `main`: Produzione stabile.
*   `feat/nome-feature`: Sviluppo nuove funzionalità.
*   `fix/descrizione-bug`: Correzioni bug.
*   `refactor/descrizione`: Miglioramenti strutturali senza cambio logica.

### Commit Messages
Formato: `type: Subject`
*   `feat`: Nuova funzionalità.
*   `fix`: Correzione bug.
*   `docs`: Aggiornamento documentazione.
*   `refactor`: Refactoring codice.
*   `test`: Aggiunta/Modifica test.
*   `chore`: Aggiornamento dipendenze, build tools.

*Esempio*: `feat: Implement robust retry logic for AI extraction`

## 4. Gestione Errori

*   **No Silent Failures**: Vietato `except Exception: pass`. Logga sempre l'errore.
*   **UI Feedback**: Ogni errore critico deve essere comunicato all'utente in italiano (es. "Errore di connessione al server") e non con stack trace tecnici.

## 5. Testing Policy

Il progetto adotta la **Green Suite Policy**.
*   Esegui `pytest` prima di ogni push.
*   Per la UI, usa `tests/desktop_app/mock_qt.py` per testare la logica senza display.
*   Non committare codice rotto.

---

## 6. Widget Safety Rules (CRASH ZERO)

Per prevenire crash da widget distrutti, segui queste regole:

### 6.1 Decorator obbligatorio per Slot

Tutti i metodi connessi a segnali devono usare `@guard_widget_access`:

```python
from desktop_app.core.widget_guard import guard_widget_access

class MyView(QWidget):
    @guard_widget_access
    def on_button_clicked(self):
        self.label.setText("Clicked!")
```

### 6.2 SafeWidgetMixin per View

Ogni view deve estendere `SafeWidgetMixin`:

```python
from desktop_app.mixins.safe_widget_mixin import SafeWidgetMixin

class MyView(QWidget, SafeWidgetMixin):
    def __init__(self):
        super().__init__()
        SafeWidgetMixin.__init__(self)
```

### 6.3 Registrazione Widget Figli

Usa `register_child()` per widget che verranno acceduti in callback:

```python
self.btn = QPushButton("Submit")
self.register_child("submit_btn", self.btn)

# Accesso sicuro
btn = self.get_child("submit_btn")
if btn:
    btn.setEnabled(False)
```

---

## 7. Animation Rules

### 7.1 Usa Animation Manager

**MAI** creare `QPropertyAnimation` direttamente. Usa sempre:

```python
from desktop_app.core.animation_manager import fade_in, fade_out

fade_in(widget, duration_ms=300)
```

### 7.2 Cleanup in closeEvent

**SEMPRE** cancellare animazioni quando il widget viene distrutto:

```python
def closeEvent(self, event):
    from desktop_app.core.animation_manager import animation_manager
    animation_manager.cancel_all(self)
    super().closeEvent(event)
```

### 7.3 No Animazioni su Widget Distrutti

Verifica sempre che il widget sia valido prima di animare:

```python
from desktop_app.core.widget_guard import is_widget_alive

if is_widget_alive(widget):
    fade_out(widget)
```

---

## 8. Signal/Slot Rules

### 8.1 Usa ConnectionTracker

Per view con molte connessioni, usa `ConnectionTracker`:

```python
from desktop_app.core.signal_guard import ConnectionTracker

class MyView(QWidget):
    def __init__(self):
        self._tracker = ConnectionTracker()
        self._tracker.connect(btn.clicked, self.on_click)
    
    def closeEvent(self, event):
        self._tracker.disconnect_all()
```

### 8.2 Connessioni Uniche

Evita connessioni duplicate con `UniqueConnection`:

```python
btn.clicked.connect(self.handler, Qt.ConnectionType.UniqueConnection)
```

### 8.3 Disconnessione Sicura

Usa `safe_disconnect` per evitare errori su segnali già disconnessi:

```python
from desktop_app.core.signal_guard import safe_disconnect

safe_disconnect(btn.clicked, self.handler)  # Non fallisce se già disconnesso
```

---

## 9. Error Boundary Rules

### 9.1 Ogni View ha un ErrorBoundary

```python
from desktop_app.core.error_boundary import ErrorBoundary

class MyView(QWidget):
    def __init__(self):
        self._error_boundary = ErrorBoundary("MyView")
```

### 9.2 Proteggi Operazioni Critiche

```python
def load_data(self):
    with self._error_boundary.protect():
        data = self.api.get_data()
        self.display(data)
```

*Per documentazione completa, vedi [CRASH_ZERO_ARCHITECTURE.md](CRASH_ZERO_ARCHITECTURE.md).*
