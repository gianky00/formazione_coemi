# Struttura del Progetto e Copertura dei Test

Questo documento fornisce una mappatura tecnica completa ed estremamente dettagliata della struttura del repository `intelleo`, inclusi backend, frontend desktop, frontend guida, script amministrativi e suite di test.

## 1. Backend (`app/`)
Il backend è un'applicazione FastAPI "Headless" responsabile della logica di business, persistenza, sicurezza e servizi AI.

### Struttura Directory
*   **`app/api/`**: Definizione ed esposizione endpoint.
    *   `routers/`: Moduli di routing segregati (`auth.py`, `users.py`, `notifications.py`, `certificati.py`, `system.py`).
    *   `deps.py`: Dependency Injection (Sessioni DB, User Auth, Admin Permissions).
    *   `main.py`: Entry point FastAPI. Gestisce `Lifespan` (Startup/Shutdown), Middleware (CORS, Errori) e inizializzazione `APScheduler`.
*   **`app/core/`**: Infrastruttura critica e Sicurezza.
    *   `config.py`: Gestore configurazione (`SettingsManager`). Separa segreti statici (Environment) da configurazioni mutabili (`settings.json`).
    *   `security.py`: Primitive crittografiche (Bcrypt, JWT).
    *   `db_security.py`: `DBSecurityManager`. Gestisce il caricamento/salvataggio del DB cifrato in memoria e il monitoraggio integrità.
    *   `lock_manager.py`: Gestione Lock OS-Level (`Portalocker`) per prevenire accessi concorrenti al file DB.
    *   `license_security.py`: Logica di verifica crittografica (Fernet) per le licenze.
*   **`app/db/`**: Livello Dati (SQLAlchemy).
    *   `models.py`: Definizione ORM (`User`, `Dipendente`, `Certificato`, `Corso`, `AuditLog`).
    *   `session.py`: Factory sessioni e Engine (configurato per `StaticPool` in-memory).
    *   `seeding.py`: Logica di popolamento iniziale e migrazione schema "Smart".
*   **`app/services/`**: Logica di Business Pura.
    *   `ai_extraction.py`: Client Gemini (Single-pass extraction). Gestisce prompt engineering e retry (`Tenacity`).
    *   `certificate_logic.py`: Calcolo scadenze e stati (`Attivo`, `Scaduto`, `In Scadenza`).
    *   `notification_service.py`: Generazione Report PDF (`FPDF`) e invio Email (`SMTP` con auto-detection SSL/TLS).
    *   `document_locator.py`: Astrazione Filesystem. Gestisce percorsi relativi/assoluti e organizzazione cartelle.
    *   `matcher.py`: Risoluzione identità dipendenti (Fuzzy Matching + Date of Birth).
    *   `file_maintenance.py`: Archiviazione automatica certificati scaduti.

---

## 2. Desktop Application (`desktop_app/`)
Frontend PyQt6. Architettura MVVM-Lite con Controller centrale.

### Struttura Directory
*   **`desktop_app/views/`**: Componenti UI (Widgets).
    *   `login_view.py`: Form login con visualizzazione stato licenza e lock DB.
    *   `dashboard_view.py`: Griglia dati principale (`QTableView`).
    *   `scadenzario_view.py`: Gantt Chart (`QGraphicsScene`) e Timeline.
    *   `import_view.py`: Area Drag & Drop con feedback visuale.
    *   `validation_view.py`: Interfaccia di convalida manuale (Pillole di stato).
    *   `config_view.py`: Pannello impostazioni (SMTP, Backup, Password).
    *   `modern_guide_view.py`: Wrapper `QWebEngineView` per `guide_frontend`.
*   **`desktop_app/view_models/`**: Logica di presentazione.
    *   `dashboard_view_model.py`: Filtri avanzati e gestione dati per la Dashboard.
*   **`desktop_app/services/`**: Servizi Client-Side.
    *   `api_client.py`: Wrapper HTTP (`Requests`). Gestisce Token JWT e Header Auth.
    *   `hardware_id_service.py`: Fingerprinting Hardware (WMI Disk Serial / MAC).
    *   `license_manager.py`: Verifica locale licenza (`config.dat`).
    *   `license_updater_service.py`: Pipeline Auto-Update (GitHub -> Local).
    *   `time_service.py`: Anti-tamper temporale (NTP vs Secure Cache).
    *   `integrity_service.py`: Checksum verification dei componenti core.
*   **`desktop_app/workers/`**: Concorrenza (`QRunnable` / `QThread`).
    *   `file_scanner_worker.py`: Scansione asincrona file system.
    *   `chat_worker.py`: Gestione streaming risposte AI.
*   **`desktop_app/components/`**: Widget Riutilizzabili.
    *   `neural_3d.py`: Visualizzazione grafica animata.
    *   `toast.py`: Notifiche non intrusive.
    *   `custom_dialog.py`: Finestre di dialogo standardizzate.
*   **`desktop_app/chat/`**: Logica Assistente Lyra.
    *   `chat_controller.py`: Gestione stato conversazione e RAG.
    *   `phonetic_utils.py`: Correzione fonetica per TTS.

---

## 3. Guide Frontend (`guide_frontend/`)
Manuale utente moderno, Mobile-Responsive.

*   **Tecnologia**: React 18 + Vite + TailwindCSS v3.
*   **Integrazione**: Compilato in `dist/` e servito via `file://` in `QWebEngineView`.
*   **Bridge**: Comunica con PyQt6 via `QWebChannel` (`qtwebchannel/qwebchannel.js`).

---

## 4. Admin & Build Scripts (`admin/`)
Strumenti per lo sviluppo, il deployment e la manutenzione.

*   **`admin/offusca/build_dist.py`**: **Master Build Script**.
    *   Esegue PyArmor (Offuscamento).
    *   Compila con PyInstaller (Frozen Executable).
    *   Compila Installer Inno Setup (`setup_script.iss`).
*   **`admin/crea_licenze/admin_license_gui.py`**: Generatore Licenze Admin (GUI Tkinter).
    *   Genera `pyarmor.rkey` e `config.dat` cifrato.
*   **`admin/call_list_IA.py`**: Utility CLI per testare connettività Gemini e listare modelli disponibili.
*   **`admin/riepilogo_Bug_Sonar.py`**: Analisi statica custom per reportistica bug.

---

## 5. Test Coverage (`tests/`)
Struttura speculare al codice sorgente ("Parallel Structure").

### Backend (`tests/app/`)
*   **`api/`**: Test integrazione Endpoints.
    *   Copertura totale flussi Auth, Upload, Update, Delete.
*   **`core/`**: Test Sicurezza e Infrastruttura.
    *   `test_db_security*.py`: Verifica Encryption-at-Rest, Locking, Corruption Recovery.
    *   `test_lock_manager*.py`: Verifica File Locking OS-Level.
*   **`services/`**: Unit Tests Logica Business.
    *   `test_ai_extraction.py`: Mocking risposte Gemini.
    *   `test_certificate_logic.py`: Verifica calcolo scadenze e stati.

### Frontend (`tests/desktop_app/`)
*   **Headless Testing**: Utilizza `tests/desktop_app/mock_qt.py` per simulare l'intero framework Qt (Widgets, Signals, Slots) senza display grafico.
*   **Views**:
    *   `test_scadenzario_logic.py`: Verifica logica temporale Gantt.
    *   `test_login_view_logic.py`: Verifica stati UI login.
*   **Services**:
    *   `test_license_manager.py`: Verifica parsing e decifratura licenze.
    *   `test_time_service.py`: Verifica logica NTP e Anti-Rollback.

### Tools (`tests/tools/`)
*   Verifica script di build e utility accessorie.
