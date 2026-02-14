Ecco il file `DEVELOPER_ONBOARDING.md` generato, strutturato per fornire una guida completa e immediatamente operativa per nuovi sviluppatori (sia umani che AI Agents).

```markdown
# DEVELOPER_ONBOARDING.md

# Benvenuto nel Team di Sviluppo Intelleo! 🚀

Questa guida è il punto di riferimento unico per configurare l'ambiente, comprendere l'architettura e iniziare a contribuire al progetto **Intelleo**.

Il progetto è un sistema ibrido complesso che combina:
1.  **Backend Python:** FastAPI + SQLAlchemy (SQLite criptato in-memory).
2.  **Frontend Desktop:** Tkinter (Logica principale) + Componenti Legacy/Supporto PyQt6.
3.  **Frontend Guida:** React (Vite) servito staticamente.
4.  **Sicurezza:** Crittografia custom, Offuscamento (PyArmor), Compilazione nativa (Nuitka).

---

## ✅ Checklist Primo Giorno

Completa questi passaggi in ordine per avere un ambiente funzionante.

- [ ] **Clona il repository** e naviga nella root.
- [ ] **Installa i prerequisiti** (Python, Node.js, C++ Compiler).
- [ ] **Crea l'ambiente virtuale** Python.
- [ ] **Installa le dipendenze** (`pip install -r requirements.txt`).
- [ ] **Compila il Frontend Guida** (React).
- [ ] **Configura le API Key** (Google Gemini).
- [ ] **Esegui il primo avvio** (`launcher.py`).
- [ ] **Esegui i test** per verificare l'integrità.

---

## 🛠️ Prerequisiti Software

Assicurati di avere installato il seguente software. **Le versioni sono critiche** per la compatibilità con Nuitka e PyArmor.

| Software | Versione Richiesta | Scopo | Comando Verifica |
| :--- | :--- | :--- | :--- |
| **Python** | **3.12.x** (64-bit) | Runtime principale | `python --version` |
| **Node.js** | 18+ (LTS) | Build `guide_frontend` | `node -v` |
| **Git** | Latest | Version Control | `git --version` |
| **MSVC Build Tools** | 2022 (v143+) | Compilazione Nuitka (C++) | `cl.exe` (da dev cmd) |
| **Inno Setup** | 6.2+ | Creazione Installer Windows | `ISCC.exe` |

---

## 🚀 Step-by-Step Setup

Esegui questi comandi in una shell (PowerShell o CMD) con privilegi utente standard.

### 1. Setup Ambiente Python
```powershell
# 1. Crea virtual environment (raccomandato)
python -m venv venv

# 2. Attiva environment
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
# source venv/bin/activate

# 3. Aggiorna pip e installa dipendenze
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 2. Setup Frontend Guida (React)
Il modulo "Guida" è una SPA React che deve essere compilata prima dell'uso.

```powershell
cd guide_frontend
npm install
npm run build
cd ..
# Verifica: deve esistere guide_frontend/dist/index.html
```

### 3. Configurazione Variabili d'Ambiente
Crea un file `.env` (o imposta le variabili di sistema) se necessario, ma per lo sviluppo locale puoi anche affidarti ai default di `app/core/config.py`.

**Critico:** Per far funzionare l'analisi AI e la Chat, devi impostare le chiavi Google Gemini.
*Nota: Nel codice (`config.py`), le chiavi sono spesso offuscate (`obf:...`). In dev, puoi passarle in chiaro nelle variabili d'ambiente.*

```powershell
set GEMINI_API_KEY_ANALYSIS="la_tua_chiave_google_ai"
set GEMINI_API_KEY_CHAT="la_tua_chiave_google_ai"
```

### 4. Primo Avvio
Avvia l'applicazione tramite il launcher (simula l'avvio dell'EXE finale).

```powershell
python launcher.py
```
*Se tutto funziona, vedrai la finestra di login di Intelleo.*
*Credenziali Default (se create dal seeding):* `admin` / `prova` (o `primoaccesso`).

---

## 🔧 Troubleshooting Setup Comuni

| Errore / Sintomo | Causa Probabile | Soluzione |
| :--- | :--- | :--- |
| `ModuleNotFoundError: No module named 'app'` | `PYTHONPATH` non impostato | Esegui `set PYTHONPATH=.` nella root prima di lanciare python. |
| `ImportError: DLL load failed` (PyQt6) | Mancanza DLL di sistema | Installa VC++ Redistributable 2015-2022. |
| `Database Locked` / `Sola Lettura` | Lock file residuo | Cancella il file `.database_documenti.db.lock` nella cartella dati (vedi `get_user_data_dir`). |
| `Nuitka: fatal error C1083` | Mancano header C++ | Installa "Desktop development with C++" da Visual Studio Installer. |
| `npm` non trovato | Node.js mancante | Installa Node.js e riavvia la shell. |

---

## 🏗️ Architettura in 5 Minuti

Intelleo segue un'architettura **Monolito Modulare Ibrido**.

```mermaid
graph TD
    User[Utente Desktop] --> Launcher[Launcher.py]

    subgraph "Runtime Process"
        Launcher -->|Avvia Thread| API[FastAPI Backend :8000]
        Launcher -->|Avvia MainThread| UI[Tkinter Frontend]
    end

    subgraph "Data Layer"
        API -->|SQLAlchemy| DBSec[DBSecurityManager]
        DBSec -->|Decrypt in RAM| SQLite[(SQLite In-Memory)]
        DBSec -->|Encrypt on Save| FileDB[database_documenti.db (Disk)]
    end

    subgraph "External Services"
        API -->|HTTP| Gemini[Google Gemini AI]
        API -->|SMTP| Email[Server Posta]
    end

    UI -->|HTTP Requests| API
    UI -->|Load HTML| Guide[React SPA (Guide)]
```

### Concetti Chiave:
1.  **Backend-for-Frontend:** Il backend FastAPI gira *localmente* (localhost) nello stesso processo/macchina della UI.
2.  **Sicurezza DB:** Il database su disco è cifrato (AES/Fernet). Viene decifrato *solo in RAM* all'avvio (`app/core/db_security.py`).
3.  **Locking:** Un sistema di lock basato su file (`app/core/lock_manager.py`) impedisce l'apertura multipla del DB, forzando la modalità "Sola Lettura" per le istanze secondarie.
4.  **Frontend Ibrido:** La UI principale è **Tkinter** (`desktop_app`), ma usa asset generati da **PyQt** (`tools/prepare_installer_assets.py`) e visualizza guide HTML complesse.

---

## 💻 Workflow Sviluppo

### Struttura Branch
*   `main`: Codice di produzione stabile.
*   `develop`: Branch di integrazione.
*   `feature/nome-feature`: Sviluppo nuove funzionalità.

### Come Sviluppare una Feature
1.  **Backend:** Modifica `app/api/routers/` e `app/services/`.
    *   *Test:* Esegui `pytest tests/app/` per verificare la logica.
2.  **Frontend:** Modifica `desktop_app/views/`.
    *   *Nota:* Tkinter non ha hot-reload. Devi riavviare `launcher.py`.
3.  **Migrazioni DB:** Non usiamo Alembic. Le modifiche allo schema vanno gestite in `app/db/seeding.py` -> `migrate_schema()`.

### Build e Rilascio
Per creare l'eseguibile finale (Nuitka):

```powershell
# 1. Pulisci build precedenti
python admin/offusca/build_nuitka.py --clean

# 2. Compila (richiede tempo, 20-40 min)
python admin/offusca/build_nuitka.py

# 3. Crea Installer (richiede Inno Setup)
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" admin/crea_setup/setup_script.iss
```

---

## 📞 Chi Contattare

| Ruolo | Contatto | Area di Competenza |
| :--- | :--- | :--- |
| **Lead Architect** | *Vedi Git Log* | Architettura Core, Nuitka, Sicurezza |
| **Backend Dev** | *Vedi Git Log* | FastAPI, SQLAlchemy, Integrazione AI |
| **Frontend Dev** | *Vedi Git Log* | Tkinter, React Guide |
| **Supporto** | `support@intelleo.it` | Licenze, Problemi Clienti |

---

## 📚 Risorse Utili

*   **Documentazione Interna:** Cartella `docs/` (leggi `SYSTEM_ARCHITECTURE.md` e `MIGRATION_NOTES.md`).
*   **FastAPI Docs:** [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
*   **Tkinter Reference:** [tkdocs.com](https://tkdocs.com/)
*   **Nuitka User Manual:** [nuitka.net](https://nuitka.net/doc/user-manual.html)

---

## 🎯 Primi Task Suggeriti (Settimana 1)

1.  **Esplorazione:** Esegui `admin/tools/test_path_resolution_integrated.py` per capire come il software trova i file in modalità Dev vs Frozen.
2.  **Fix Minore:** Cerca nei commenti del codice `TODO` o `FIXME` e risolvine uno semplice.
3.  **Test:** Aggiungi un test case in `tests/app/api/test_main.py` per una rotta esistente.
4.  **UI:** Prova a cambiare il colore di un bottone in `desktop_app/views/dashboard_view.py` e verifica il risultato.

---

## ❓ FAQ (Sviluppatore)

**Q: Perché `launcher.py` avvia un thread separato per Uvicorn?**
A: Per permettere a Backend e Frontend di coesistere nello stesso processo ed essere distribuiti come singolo EXE, evitando la complessità di gestire due eseguibili separati.

**Q: Cos'è `pyarmor.rkey`?**
A: È il file di licenza generato da PyArmor. Senza di esso (o se non valido), l'applicazione non parte o ha funzionalità limitate. In dev, il check è spesso bypassato o mockato nei test.

**Q: Ho modificato il DB ma i dati sono spariti al riavvio. Perché?**
A: Verifica `app/core/db_security.py`. Se il `save_to_disk()` fallisce (es. permessi, read-only mode), il DB in RAM viene perso alla chiusura. Controlla i log (`intelleo.log`).

**Q: Come faccio a vedere i log?**
A: I log vengono scritti in `%LOCALAPPDATA%\Intelleo\logs\intelleo.log`. In console vedrai solo messaggi di livello WARNING o superiore di default.
```
