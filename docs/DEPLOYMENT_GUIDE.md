Ecco il file **DEPLOYMENT_GUIDE.md**, redatto con un livello di dettaglio estremo, analizzando l'architettura ibrida (Python Backend + Tkinter Desktop + React Frontend) del progetto Intelleo.

***

# DEPLOYMENT_GUIDE.md - Guida Completa al Deployment e Distribuzione

## 📖 Introduzione
Questa guida documenta l'intero ciclo di vita del deployment per **Intelleo**, un'applicazione desktop ibrida che incapsula un backend FastAPI, un frontend React (Guida) e un'interfaccia nativa Tkinter, compilati in un unico eseguibile Windows tramite **Nuitka**.

---

## 1. 🌍 Ambienti

Poiché Intelleo è un'applicazione desktop distribuita on-premise (sui PC dei clienti), i concetti di ambiente differiscono dal web standard.

| Ambiente | Descrizione | Configurazione | Build Flag |
|----------|-------------|----------------|------------|
| **Development** | Esecuzione da sorgente (`launcher.py`). Hot-reload attivo per React. | `DEBUG=True`, `API_URL=http://localhost:8000` | N/A |
| **Staging (Test Build)** | Eseguibile compilato ma non firmato/offuscato. Usato per test interni su VM pulite. | `DEBUG=False`, Console visibile (opzionale) | `python build_nuitka.py --fast` |
| **Production** | Eseguibile finale, ottimizzato (LTO), offuscato, con installer Inno Setup. | `DEBUG=False`, No Console, Sentry Attivo | `python build_nuitka.py --clean` |

---

## 2. 🏗️ Prerequisiti Infrastruttura (Build Machine)

Per compilare l'applicazione è necessaria una macchina Windows (fisica o CI/CD runner) con le seguenti specifiche.

### Software Richiesto
1.  **OS:** Windows 10/11 SDK (x64).
2.  **Python:** Versione **3.12+** (Tassativo, vedi `build_nuitka.py`).
3.  **Compilatore C:**
    *   **Microsoft Visual C++ (MSVC)** 14.3+ (Incluso in Visual Studio Build Tools 2022).
    *   Necessario per la compilazione statica di Nuitka.
4.  **Node.js & NPM:**
    *   Richiesto per buildare `guide_frontend`.
    *   Versione raccomandata: LTS (v18+).
5.  **Inno Setup 6.2+:**
    *   Necessario per generare l'installer `.exe`.
    *   Path standard: `C:\Program Files (x86)\Inno Setup 6\ISCC.exe`.
6.  **Git:** Per il versionamento.

### Python Packages (Build Dependencies)
Installare i requisiti globali o in venv prima del build:
```bash
pip install -r requirements.txt
pip install nuitka zstandard ordered-set  # Nuitka dependencies
pip install pyarmor                       # Se si usa l'offuscamento extra
```

---

## 3. ⚙️ Configurazione per Ambiente

La configurazione è gestita su tre livelli: **Hardcoded (Sicurezza)**, **File (Mutable)**, e **Variabili d'Ambiente (Build)**.

### A. Segreti e Offuscamento (Build Time)
I segreti non devono mai essere in chiaro. Prima del build, usare il tool dedicato:
```bash
python admin/tools/generate_obfuscated_keys.py
```
Questo genera stringhe come `obf:ZmFrZV...` da incollare in `app/core/config.py`.
*   **Chiavi Critiche:** `FERNET_KEY` (Licenze), `GITHUB_TOKEN` (Aggiornamenti), `GEMINI_API_KEY`.

### B. Runtime Settings (`settings.json`)
L'app crea/legge `%LOCALAPPDATA%\Intelleo\settings.json`.
*   **Non deployare questo file.** Viene generato al primo avvio.
*   Contiene: Configurazione SMTP, path database custom, preferenze utente.

### C. Variabili d'Ambiente (CI/CD)
Per la pipeline di build (es. GitHub Actions):
*   `SENTRY_DSN`: DSN per il tracciamento errori in produzione.
*   `IA_API_KEY`: Chiave Google Gemini per i test di integrazione pre-build.

---

## 4. 🛠️ Build Process (Workflow Completo)

Il processo è orchestrato dallo script master `admin/offusca/build_nuitka.py`.

### Diagramma di Flusso Build
```mermaid
graph TD
    A[Start Build] --> B{Check Env}
    B -- Fail --> C[Error Exit]
    B -- OK --> D[Build React Frontend]
    D --> E[Prepare Assets & Obfuscation]
    E --> F[Nuitka Compilation (Python -> C -> Exe)]
    F --> G[Post-Processing (DLLs, README)]
    G --> H[Inno Setup (Create Installer)]
    H --> I[Final Artifact: Setup.exe]
```

### Comandi Manuali Passo-Passo

#### 1. Build Frontend (React)
Compila la SPA della guida utente.
```bash
cd guide_frontend
npm install
npm run build
# Output atteso: guide_frontend/dist/index.html
cd ..
```

#### 2. Preparazione Asset
Genera le immagini per l'installer (BMP) e verifica l'integrità.
```bash
python tools/prepare_installer_assets.py
```

#### 3. Compilazione Core (Nuitka)
Questo step compila Python in codice macchina.
*   **Modalità Produzione (Lenta, Ottimizzata):**
    ```bash
    python admin/offusca/build_nuitka.py --clean
    ```
*   **Modalità Test (Veloce, No LTO):**
    ```bash
    python admin/offusca/build_nuitka.py --fast
    ```

**Dettagli Nuitka:**
*   Entry point: `launcher.py`
*   Modalità: `--standalone` (include interprete)
*   Plugin: `pyqt6` (anche se si usa Tkinter, per compatibilità legacy o moduli residui), `numpy`.
*   Inclusioni forzate: `uvicorn`, `fastapi`, `sqlalchemy`, `google.generativeai`.

#### 4. Creazione Installer
Impacchetta la cartella `dist/nuitka/Intelleo.dist` in un singolo setup.
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" admin/crea_setup/setup_script.iss
```
*   **Output:** `dist/installer/Intelleo_Setup_vX.X.X.exe`

---

## 5. 🚀 CI/CD Pipeline (Suggerita)

File: `.github/workflows/build_windows.yml`

### Stages
1.  **Test:** Esegue `pytest tests/` su ogni push.
2.  **Security Audit:** Esegue `python admin/tools/security_audit.py` per cercare chiavi in chiaro.
3.  **Build:** Esegue `build_nuitka.py` solo su tag `v*` o push su `main`.
4.  **Sign:** (Opzionale) Firma l'eseguibile con `signtool` e certificato EV.
5.  **Release:** Carica l'installer su GitHub Releases (usato dall'updater interno).

### Triggers
*   `push`: branches `main`
*   `pull_request`: branches `main`
*   `workflow_dispatch`: Manuale

---

## 6. 📦 Deployment Steps (Installazione Cliente)

Poiché è un'app desktop, il "deploy" è l'installazione.

1.  **Distribuzione:** Inviare `Intelleo_Setup_v2.0.0.exe` al cliente (via Link sicuro, NAS, o GitHub Release).
2.  **Installazione:**
    *   Eseguire il setup come Amministratore.
    *   Directory default: `C:\Program Files\Intelleo`.
3.  **Primo Avvio (Attivazione):**
    *   L'app mostrerà il **Hardware ID**.
    *   L'amministratore deve generare la licenza usando `admin/crea_licenze/admin_license_gui.py`.
    *   Copiare i file di licenza (`config.dat`, `pyarmor.rkey`) in `%LOCALAPPDATA%\Intelleo\Licenza`.
4.  **Database:**
    *   Al primo avvio, l'app chiederà se creare un nuovo DB o collegarne uno esistente.
    *   Selezionare un percorso di rete (es. `Z:\Intelleo_DB`) se multi-utente.

---

## 7. 🔙 Rollback Procedure

In caso di versione instabile rilasciata ai clienti:

1.  **Identificare la versione stabile precedente** (es. v1.9.0).
2.  **Disinstallazione:** Pannello di Controllo -> Disinstalla Intelleo.
    *   *Nota:* Questo **NON** cancella i dati (`%LOCALAPPDATA%` o il DB su rete). I dati sono salvi.
3.  **Reinstallazione:** Installare la versione v1.9.0.
4.  **Compatibilità DB:** Se la v2.0.0 ha applicato migrazioni DB irreversibili (raro con SQLite/SQLAlchemy in questo setup, ma possibile), ripristinare il backup automatico del DB che si trova in `Backups/` accanto al file `.db`.

---

## 8. 🩺 Health Checks & Monitoring

Non essendoci un server centrale, il monitoraggio è distribuito.

### Endpoint Locali
L'app espone API locali per diagnostica (solo localhost):
*   `GET http://127.0.0.1:[PORT]/api/v1/health`: Stato del backend.
*   `GET http://127.0.0.1:[PORT]/api/v1/system/lock-status`: Verifica se il DB è bloccato (ReadOnly).

### Telemetria Remota
*   **Sentry:** Cattura crash Python non gestiti e panic del backend. Configurato in `app/main.py`.
*   **Audit Logs:** Ogni azione critica (Login, Delete, Update) è salvata nella tabella `audit_logs` del DB locale del cliente.

---

## 9. 📈 Scaling

*   **Verticale:** L'app usa SQLite In-Memory. Le performance dipendono dalla RAM del client. Per database > 2GB, aumentare la RAM del client.
*   **Orizzontale (Multi-Utente):**
    *   Intelleo usa un sistema di **File Locking** (`app/core/lock_manager.py`).
    *   Solo **1 utente** alla volta può scrivere (RW).
    *   Gli altri utenti entrano in modalità **Sola Lettura** (RO).
    *   *Scaling Limit:* Non progettato per >5-10 utenti concorrenti sullo stesso file DB di rete.

---

## 10. 🔧 Troubleshooting Post-Deploy

### Problema: "Database Locked" o "Sola Lettura"
*   **Causa:** Un altro utente ha il file aperto o un processo è crashato lasciando il file `.lock`.
*   **Soluzione:**
    1.  Verificare chi è il "Lock Owner" (mostrato nella UI di login).
    2.  Se il processo è morto, cancellare manualmente il file `.database_documenti.db.lock` nella cartella del DB.
    3.  Il sistema ha un'auto-recovery per "Stale Locks" (PID inesistenti), riavviare l'app potrebbe risolvere.

### Problema: "Dll load failed" o "Module not found"
*   **Causa:** Build Nuitka incompleto o VC++ Redistributable mancante.
*   **Soluzione:**
    1.  Installare VC++ Redist 2015-2022 sul client.
    2.  Verificare i log in `%LOCALAPPDATA%\Intelleo\logs\intelleo.log`.

### Problema: Aggiornamento Licenza Fallito
*   **Causa:** Firewall blocca GitHub API o token scaduto.
*   **Soluzione:** Aggiornare manualmente copiando i file in `%LOCALAPPDATA%\Intelleo\Licenza`.

---

## 11. ✅ Post-Deployment Checklist

Da eseguire sulla macchina del cliente o in ambiente di staging prima del rilascio:

- [ ] **Avvio:** L'applicazione si avvia in < 5 secondi?
- [ ] **Licenza:** Viene riconosciuta correttamente (non mostra "Trial" o errori)?
- [ ] **DB:** Si connette al database (nuovo o esistente)?
- [ ] **Backend:** La chiamata a `/health` risponde `{"status": "ok"}`?
- [ ] **AI:** L'upload di un PDF di test estrae i dati correttamente (verifica connessione Gemini)?
- [ ] **Frontend:** La sezione "Guida" si apre correttamente (verifica caricamento asset React)?
- [ ] **Chiusura:** L'applicazione si chiude pulitamente senza lasciare processi `Intelleo.exe` appesi?
- [ ] **Disinstallazione:** L'uninstaller rimuove i file di programma ma preserva i dati utente?
