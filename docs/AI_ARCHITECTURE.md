Ecco il file `AI_ARCHITECTURE.md`, generato basandosi sull'analisi approfondita del codice sorgente fornito.

***

# AI_ARCHITECTURE.md

## 1. Executive Summary

**Progetto:** Intelleo
**Versione:** 1.0.0 (Core) / 2.0.0 (Build System Nuitka)
**Tipologia:** Desktop Application Ibrida (Local Client-Server)

**Intelleo** è una soluzione software avanzata per la gestione della sicurezza sul lavoro, specializzata nel monitoraggio delle scadenze, nella formazione del personale e nella gestione documentale. L'applicazione utilizza un'architettura ibrida unica che combina un'interfaccia desktop nativa (Tkinter) con un backend locale (FastAPI), sfruttando l'Intelligenza Artificiale (Google Gemini) per l'estrazione automatica dei dati dai documenti PDF.

**Punti di Forza Architetturali:**
*   **Sicurezza dei Dati:** Utilizza un database SQLite criptato (AES-256 via Fernet) che risiede su disco ma viene decriptato e caricato interamente in memoria (RAM) durante l'esecuzione, garantendo velocità e sicurezza "at-rest".
*   **AI-Driven:** Integrazione profonda con LLM per parsing di documenti non strutturati e assistenza via chat (RAG - Retrieval Augmented Generation).
*   **Protezione IP:** Pipeline di build basata su **Nuitka** (compilazione C) e **PyArmor** (offuscamento bytecode) per la massima protezione della proprietà intellettuale.
*   **Robustezza:** Sistema di *Crash-Safe Locking* per prevenire corruzione dati in scenari multi-processo o crash improvvisi.

---

## 2. Stack Tecnologico Completo

| Categoria | Tecnologia | Versione Rilevata | Scopo | Note |
|-----------|------------|-------------------|-------|------|
| **Linguaggio** | Python | 3.12.10 | Core Logic | |
| **Backend Framework** | FastAPI | 0.121.2 | API Server Locale | Espone endpoint su `localhost` |
| **Server WSGI/ASGI** | Uvicorn | 0.38.0 | Server HTTP | Esegue in thread separato dal launcher |
| **Database** | SQLite | 3.x | Storage Dati | Gestito tramite `sqlite3` e `SQLAlchemy` |
| **ORM** | SQLAlchemy | 2.0.44 | Abstraction Layer | Usa `StaticPool` per connessione in-memory persistente |
| **Frontend Desktop** | Tkinter | (Stdlib) | GUI Principale | Gestita in `desktop_app` |
| **Frontend Guida** | React | 19.2.0 | Guida Interattiva | Buildata con Vite, servita come asset statico |
| **AI & LLM** | Google GenAI | 0.8.5 | OCR & Chatbot | Modelli: `gemini-2.5-pro` (Analisi), `gemini-2.5-flash` (Chat) |
| **Sicurezza** | Cryptography | - | Cifratura DB | Fernet (Simmetrica) |
| **Compilazione** | Nuitka | 2.0.0+ | Compilazione EXE | Converte Python in C per performance e protezione |
| **Offuscamento** | PyArmor | - | Protezione Script | Protezione aggiuntiva pre-compilazione |
| **Packaging** | Inno Setup | 6.2+ | Installer Windows | Genera `setup.exe` |
| **Testing** | Pytest | 9.0.1 | Unit & Integration | Copertura estesa su API e Core |
| **Logging** | Sentry SDK | - | Error Tracking | DSN offuscato nel codice |
| **TTS** | gTTS / PyGame | - | Text-to-Speech | Feedback vocale (Assistente Lyra) |

---

## 3. Struttura Directory Completa

```text
formazione_coemi/
├── admin/                  # Script di amministrazione e tool interni
│   ├── crea_licenze/       # GUI e logica per generare licenze clienti
│   ├── crea_setup/         # Script Inno Setup (.iss) per l'installer
│   ├── offusca/            # Pipeline di build Nuitka e PyArmor
│   ├── token_injector/     # Tool per iniettare token GitHub offuscati
│   └── tools/              # Script di utilità (benchmark, audit sicurezza, test manuali)
├── app/                    # BACKEND (FastAPI)
│   ├── api/                # Router e Endpoints (auth, users, certificati, chat)
│   ├── core/               # Logica core (config, security, lock manager)
│   ├── db/                 # Modelli SQLAlchemy e session management
│   ├── schemas/            # Modelli Pydantic (Request/Response)
│   ├── services/           # Business Logic (AI extraction, Email, File Sync)
│   └── utils/              # Utility (Date parsing, logging, audit)
├── desktop_app/            # FRONTEND (Tkinter)
│   ├── components/         # Widget riutilizzabili (non molto usati in Tkinter puro, legacy PyQt)
│   ├── services/           # Servizi lato client (API Client, Hardware ID, TTS)
│   ├── views/              # Schermate della GUI (Login, Dashboard, DatabaseView)
│   ├── workers/            # Thread worker per operazioni lunghe (non bloccanti)
│   ├── api_client.py       # Wrapper requests per comunicare con il backend
│   └── main.py             # Entry point della GUI Tkinter
├── guide_frontend/         # Progetto React (Vite) per la guida utente
├── tests/                  # Suite di test Pytest
├── tools/                  # Script di utilità root (build_guide, prepare_assets)
├── boot_loader.py          # Wrapper di sicurezza per l'avvio (gestione crash nativa)
├── launcher.py             # ENTRY POINT PRINCIPALE: Avvia Backend + Frontend
└── requirements.txt        # Dipendenze Python
```

---

## 4. Componenti e Moduli Principali

### 4.1. Launcher (`launcher.py`)
È il punto di ingresso dell'eseguibile.
*   **Responsabilità:**
    1.  Configura il logging globale.
    2.  Trova una porta libera (range 8000-8010).
    3.  Avvia il server FastAPI (`app.main:app`) in un **thread demone**.
    4.  Attende che il server sia pronto (polling su `localhost:port/health`).
    5.  Avvia l'interfaccia grafica (`desktop_app.main:ApplicationController`).
*   **Pattern:** Orchestrator / Bootstrap.

### 4.2. Database Security Manager (`app.core.db_security`)
Il componente più critico del sistema.
*   **Responsabilità:** Gestisce il ciclo di vita del database criptato.
*   **Funzionamento:**
    *   *Load:* Legge il file cifrato da disco -> Decripta con Fernet -> Carica in SQLite In-Memory (`conn.deserialize`).
    *   *Locking:* Acquisisce un lock su file system (`.lock`) per garantire accesso esclusivo (Single Writer). Se il lock fallisce, il sistema va in **Read-Only**.
    *   *Save:* Serializza la memoria (`conn.serialize`) -> Cripta -> Scrive su disco atomicamente.
    *   *Backup:* Esegue backup rotativi automatici all'avvio.

### 4.3. AI Extraction Service (`app.services.ai_extraction`)
Modulo di interfaccia con Google Gemini.
*   **Responsabilità:** Estrarre dati strutturati (JSON) da PDF non strutturati.
*   **Logica:**
    *   Utilizza `tenacity` per retry policy robuste (es. quota exceeded).
    *   Gestisce un prompt complesso per categorizzare i documenti (es. "ANTINCENDIO", "VISITA MEDICA").
    *   Implementa un parsing JSON resiliente per pulire l'output dell'LLM (che spesso include markdown).
    *   Utilizza un **Global Lock** (`ai_global_lock`) per evitare race condition nella configurazione della libreria `genai` tra thread di chat e thread di estrazione.

### 4.4. API Client (`desktop_app.api_client.py`)
Il ponte tra Frontend e Backend.
*   **Responsabilità:** Astrarre le chiamate HTTP verso `localhost`.
*   **Features:**
    *   Gestione automatica del token JWT (Bearer Auth).
    *   Iniezione header `X-Device-ID`.
    *   Gestione centralizzata degli errori di connessione.

---

## 5. Diagramma Architetturale (Mermaid)

```mermaid
graph TD
    User[Utente] --> GUI[Desktop App (Tkinter)]
    
    subgraph "Processo Locale (Intelleo.exe)"
        GUI -- "HTTP Requests (JSON)" --> API_Client
        API_Client -- "Localhost:8000" --> FastAPI[FastAPI Server]
        
        subgraph "Backend Core"
            FastAPI --> Auth[Auth Service]
            FastAPI --> Logic[Business Logic]
            Logic --> AIService[AI Service]
            Logic --> EmailService[Notification Service]
            Logic --> DB_Mgr[DB Security Manager]
        end
        
        subgraph "Data Layer"
            DB_Mgr -- "Deserialize/Decrypt" --> InMemoryDB[(SQLite In-Memory)]
            DB_Mgr -- "Serialize/Encrypt" --> EncryptedFile[database.db (Encrypted)]
            Lock[File Lock (.lock)] -.-> DB_Mgr
        end
    end
    
    subgraph "External Services"
        AIService -- "API Call" --> Gemini[Google Gemini API]
        EmailService -- "SMTP" --> MailServer[SMTP Server (Gmail/Aruba)]
        GUI -- "Check Update" --> GitHub[GitHub Releases]
    end

    GUI -.-> |"WebEngine (Optional)"| ReactGuide[React Guide (Static)]
```

---

## 6. Flusso Dati Dettagliato

### Flusso 1: Avvio Applicazione
1.  **Boot:** `boot_loader.py` cattura eccezioni critiche di sistema.
2.  **Launch:** `launcher.py` avvia `uvicorn` su porta 8000.
3.  **DB Init:** `app.main:lifespan` chiama `db_security.load_memory_db()`.
    *   Il file su disco viene letto e decifrato.
    *   Viene popolata la connessione in-memory condivisa (`StaticPool`).
    *   Viene acquisito il lock su file system.
4.  **UI Start:** La GUI parte, controlla la licenza locale e fa il login automatico (o mostra login screen).

### Flusso 2: Importazione PDF con AI
1.  **User Action:** Drag & Drop di un PDF nella GUI.
2.  **API Call:** `POST /api/v1/upload-pdf/` invia il file binario.
3.  **Processing:**
    *   Il backend riceve il file in memoria.
    *   `ai_extraction.py` invia il contenuto a Gemini.
    *   Gemini restituisce un JSON (es. `{"nome": "Mario Rossi", "scadenza": "2025-01-01"}`).
4.  **Response:** Il backend restituisce i dati estratti alla GUI.
5.  **Confirmation:** L'utente conferma -> `POST /api/v1/certificati/` salva il record nel DB e sposta il file fisico nella cartella organizzata (`DOCUMENTI DIPENDENTI/Nome/Categoria`).

### Flusso 3: Salvataggio Dati (Persistenza)
1.  **Trigger:** Timer automatico (ogni 5 min) o Shutdown dell'app.
2.  **Serialization:** `db_security.save_to_disk()` chiama `connection.serialize()`.
3.  **Encryption:** Il blob binario viene cifrato con Fernet.
4.  **Write:** Scrittura atomica su disco (scrittura su `.swp` e poi `os.replace`).

---

## 7. Configurazione e Ambiente

### Variabili d'Ambiente (Runtime)
Il sistema configura automaticamente queste variabili in `launcher.py` per l'ambiente *frozen*:

*   `API_URL`: `http://localhost:{port}/api/v1`
*   `DATABASE_URL`: `sqlite:///{path_to_db}`
*   `GEMINI_API_KEY_ANALYSIS`: Iniettata o letta da `settings.json`.

### File di Configurazione
*   **`settings.json`** (in `%LOCALAPPDATA%/Intelleo`): Contiene le impostazioni mutabili (SMTP, Chiavi API utente, Percorsi).
*   **`config.dat`** (in `%LOCALAPPDATA%/Intelleo/Licenza`): File di licenza cifrato contenente Hardware ID e scadenza.

### Gestione Segreti
*   I token critici (es. GitHub Token per update, Fernet Key statica) sono **offuscati** nel codice sorgente usando XOR + Base64 (vedi `app/core/string_obfuscation.py`) per prevenire l'estrazione statica tramite comandi `strings`.
*   Le chiavi vengono de-offuscate solo a runtime in memoria.

---

## 8. Setup Sviluppo Passo-Passo

**Prerequisiti:** Python 3.12+, Node.js (per la guida), Visual C++ Build Tools.

1.  **Clone e Venv:**
    ```bash
    git clone <repo_url> formazione_coemi
    cd formazione_coemi
    python -m venv .
    .\Scripts\activate
    ```

2.  **Installazione Dipendenze:**
    ```bash
    pip install --upgrade pip
    pip install -r requirements.txt
    ```

3.  **Build Frontend Guida:**
    ```bash
    cd guide_frontend
    npm install
    npm run build
    cd ..
    ```

4.  **Configurazione Sviluppo:**
    Creare un file `.env` (opzionale, il sistema usa defaults) o assicurarsi che `settings.json` non esista per forzare i default.

5.  **Avvio:**
    ```bash
    python launcher.py
    ```

---

## 9. Build e Deploy

Il processo di build è completamente automatizzato tramite script Python.

### Pipeline di Build (`admin/offusca/build_nuitka.py`)
1.  **Pre-check:** Verifica ambiente, compilatore MSVC, versione Nuitka.
2.  **Frontend Build:** Esegue build di React se necessario.
3.  **Asset Prep:** Genera immagini installer (`tools/prepare_installer_assets.py`).
4.  **Compilazione Nuitka:**
    *   Compila tutto il codice Python in C.
    *   Include pacchetti nascosti (`--include-package=app`, ecc.).
    *   Incorpora dati (icone, guida HTML).
    *   Genera un singolo eseguibile (o cartella dist standalone).
5.  **Post-Processing:** Copia DLL mancanti, crea file README.
6.  **Installer:** Compila lo script Inno Setup (`admin/crea_setup/setup_script.iss`) per generare l'installer `.exe` finale.

**Comando Build:**
```bash
python admin/offusca/build_nuitka.py --clean
```

---

## 10. Decisioni Architetturali (ADR)

| ID | Decisione | Motivazione | Alternative Considerate |
|----|-----------|-------------|-------------------------|
| **ADR-001** | **Architettura Ibrida (Local Server)** | Permette di usare FastAPI e tutto l'ecosistema Python backend robusto mantenendo una GUI desktop. Facilita una futura migrazione a Web App completa. | PyInstaller puro con logica monolitica (troppo accoppiato). |
| **ADR-002** | **SQLite In-Memory + Cifratura** | Massima sicurezza. Il DB su disco è un blob illeggibile. Nessun file temporaneo in chiaro. Prestazioni elevate in lettura. | SQLCipher (complesso da compilare/distribuire su Windows). |
| **ADR-003** | **Nuitka vs PyInstaller** | Nuitka offre prestazioni migliori (codice C) e una protezione del codice sorgente molto superiore (reverse engineering difficile). | PyInstaller (facile reverse engineering dei .pyc). |
| **ADR-004** | **Tkinter per la GUI** | Incluso nella stdlib, leggero, stabile, nessun problema di licenza (vs Qt/GPL). | PyQt6 (usato inizialmente, poi scartato per complessità licenze/dll). |
| **ADR-005** | **Polling per Comunicazione UI-Backend** | Semplice da implementare, evita complessità di WebSocket o Socket.IO per un'app locale a singolo utente. | WebSocket (overkill per questo use-case). |
| **ADR-006** | **Lock File Personalizzato** | Necessario per prevenire corruzione DB in caso di avvii multipli o crash, dato l'uso di SQLite In-Memory persistito manualmente. | Lock di sistema SQLite (non sufficiente per il modello load/save intero). |