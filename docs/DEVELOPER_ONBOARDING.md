# 🚀 Developer Onboarding: Intelleo

Benvenuto nel team di sviluppo di Intelleo. Questa guida ti aiuterà a configurare l'ambiente e a comprendere l'architettura del progetto.

## 🛠 Stack Tecnologico
- **Backend**: FastAPI (Python 3.12) + SQLAlchemy + Pydantic V2
- **Database**: SQLite (con supporto a crittografia tramite PyArmor in distribuzione)
- **Frontend Desktop**: PySide6 (Qt for Python)
- **IA**: Google Gemini SDK (Analisi documenti e Assistente Virtuale)

## 🏗 Architettura del Progetto

### 1. Backend (`app/`)
Seguiamo i principi della **Clean Architecture**:
- `api/routers/`: Entry points API leggeri. Non contengono logica di business.
- `services/`: Layer dove risiede tutta la logica (es. `EmployeeService`).
- `schemas/`: Modelli Pydantic modularizzati per dominio.
- `db/models.py`: Definizioni tabelle SQLAlchemy.

### 2. Desktop App (`desktop_app/`)
L'app utilizza un'architettura **Controller-View** moderna:
- `main.py`: Entry point e gestore globale (QMainWindow).
- `api/`: Client API modularizzato. Non usare `requests` direttamente nelle view.
- `views/`: Widget PySide6 focalizzati esclusivamente sulla presentazione.
- `widgets/`: Componenti riutilizzabili (es. `DataTable`, `SearchBar`).
- `assets/styles/main.qss`: Centralizzazione dello stile tramite CSS Qt.

## 🎨 Styling (QSS)
Non usare `setStyleSheet` nel codice Python. Aggiungi le classi nel file `main.qss` e usa:
```python
btn.setProperty("class", "PrimaryButton")
```

## 🧵 Threading
Per chiamate API lunghe, usa il sistema `Worker` basato su `QThreadPool`:
```python
worker = Worker(self.controller.api_client.auth.login, user, pwd)
worker.signals.result.connect(self.on_success)
self.controller.thread_pool.start(worker)
```

## 🧪 Testing
Esegui sempre i test prima di un commit:
```bash
pytest
```
I mock per la parte GUI si trovano in `tests/desktop_app/mock_qt.py`.
