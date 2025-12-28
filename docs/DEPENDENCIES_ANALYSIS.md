Ecco l'analisi esaustiva delle dipendenze per il progetto **Intelleo**, basata sui file di configurazione (`requirements.txt`, `package.json`) e sull'analisi statica del codice sorgente fornito.

# DEPENDENCIES_ANALYSIS.md

## 1. Overview Dipendenze

Il progetto **Intelleo** è un'applicazione ibrida composta da:
1.  **Backend/Core (Python):** Gestito tramite `pip`.
2.  **Desktop GUI (Python):** Utilizza `tkinter` (libreria standard) ma con tracce di migrazione da `PyQt6`.
3.  **Frontend Guida (React):** Gestito tramite `npm`.
4.  **Build System:** Utilizza `Nuitka` per la compilazione nativa e `Inno Setup` per l'installer.

| Categoria | Totale | Package Manager | Lock File | Stato |
| :--- | :---: | :--- | :--- | :--- |
| **Python (Runtime)** | 35+ | `pip` | ❌ Assente | Gestito via `requirements.txt` |
| **Python (Dev/Build)** | ~5 | `pip` | ❌ Assente | Misto in `requirements.txt` |
| **JavaScript (Frontend)** | 8 | `npm` | ✅ `package-lock.json` | Consistente |
| **System (External)** | 3 | N/A | N/A | Inno Setup, MSVC, Git |

---

## 2. Dipendenze Runtime (Python)

Queste librerie sono necessarie per l'esecuzione dell'applicazione compilata.

| Pacchetto | Versione (Req) | Scopo | Licenza | Note Critiche |
| :--- | :--- | :--- | :--- | :--- |
| **fastapi** | `0.121.2` | Framework API Backend | MIT | Core del backend locale. |
| **uvicorn** | `0.38.0` | Server ASGI | BSD | Server per FastAPI. |
| **sqlalchemy** | `2.0.44` | ORM Database | MIT | Gestione SQLite in-memory/file. |
| **google-generativeai**| `0.8.5` | AI (LLM) | Apache 2.0 | **Critico**: Richiede API Key valida. |
| **pyarmor** | *Latest* | Sicurezza/Licensing | Proprietary | Gestione offuscamento e licenze. |
| **wmi** | *Latest* | Hardware ID | MIT | **Windows Only**. Blocca portabilità Linux/Mac. |
| **pygame** | *Latest* | Audio | LGPL | Usato in `VoiceService` per riproduzione MP3. |
| **gTTS** | `>=2.5.1` | Text-to-Speech | MIT | Dipende dalle API di Google Translate (Online). |
| **pydantic** | `2.12.4` | Validazione Dati | MIT | Validazione schemi API e Config. |
| **python-jose** | `[cryptography]` | Sicurezza JWT | MIT | Gestione token autenticazione. |
| **passlib** | `[bcrypt]` | Hashing Password | BSD | Hashing sicuro password utenti. |
| **cryptography** | *Latest* | Crittografia | Apache/BSD | Usato per cifratura DB e Licenze (Fernet). |
| **sentry-sdk** | `[fastapi]` | Monitoraggio Errori | MIT | Tracciamento crash in produzione. |
| **posthog** | *Latest* | Analytics | MIT | Telemetria utilizzo. |
| **apscheduler** | `3.10.4` | Scheduling | MIT | Task periodici (es. alert email). |
| **fpdf2** | `2.8.5` | Generazione PDF | LGPL | Creazione report scadenze. |
| **pandas** | `2.3.3` | Data Processing | BSD | Manipolazione dati complessi/Export. |

---

## 3. Dipendenze Development & Build

Strumenti necessari solo per lo sviluppo, test e compilazione.

| Pacchetto | Scopo | Contesto d'Uso |
| :--- | :--- | :--- |
| **nuitka** | Compilatore Python -> C | `admin/offusca/build_nuitka.py`. Compilazione eseguibile standalone. |
| **zstandard** | Compressione | Dipendenza di Nuitka per onefile compression. |
| **pytest** | Testing Framework | `tests/`. Esecuzione unit e integration test. |
| **pytest-cov** | Coverage | Analisi copertura codice. |
| **pytest-mock** | Mocking | Mocking di servizi esterni (AI, DB) nei test. |
| **httpx** | Test Client | Client HTTP asincrono per testare FastAPI. |

### Frontend (Node.js)
Definiti in `guide_frontend/package.json`.

| Pacchetto | Tipo | Scopo |
| :--- | :--- | :--- |
| **vite** | Dev | Build tool e dev server per la guida React. |
| **react** | Runtime | Libreria UI per la guida interattiva. |
| **tailwindcss** | Dev | Styling CSS utility-first. |
| **lucide-react** | Runtime | Set di icone. |

---

## 4. Albero Dipendenze (Principali Catene)

Visualizzazione delle dipendenze transitive critiche per la stabilità.

```mermaid
graph TD
    App[Intelleo Application] --> FastAPI
    App --> SQLAlchemy
    App --> GenAI[Google GenAI]
    App --> Security[Security Layer]
    
    FastAPI --> Starlette
    FastAPI --> Pydantic
    
    GenAI --> GRPC
    GenAI --> Protobuf
    
    Security --> Cryptography
    Security --> PyArmor
    Security --> Jose[Python-Jose]
    
    App --> Audio[Voice Service]
    Audio --> gTTS[Google TTS]
    Audio --> Pygame
    
    App --> Sys[System]
    Sys --> WMI[WMI (Win32)]
    Sys --> PsUtil
```

---

## 5. Analisi Licenze

### Rischi Identificati
1.  **Pygame (LGPL):**
    *   L'uso di `pygame` (LGPL) in un'applicazione distribuita come eseguibile statico (via Nuitka/PyInstaller) può richiedere attenzione. Se linkato staticamente, potrebbe imporre il rilascio del codice sorgente o la possibilità per l'utente di sostituire la libreria.
    *   *Mitigazione:* Assicurarsi che `pygame` sia linkato dinamicamente (file `.pyd`/`.dll` separati nella dist) o sostituirlo con librerie più permissive (es. `playsound` o `miniaudio`).

2.  **PyArmor (Proprietary):**
    *   Richiede una licenza valida per la distribuzione commerciale se si usa la versione Pro/Enterprise per funzionalità avanzate. Il file `pyarmor.rkey` suggerisce l'uso attivo.

3.  **gTTS (MIT) ma API non ufficiale:**
    *   `gTTS` usa l'API di Google Translate non documentata. Non è un problema di licenza software, ma di **Termini di Servizio (ToS)** di Google. L'uso intensivo potrebbe portare al ban dell'IP aziendale.

---

## 6. Vulnerabilità Note e Sicurezza

| Libreria | Severità | Descrizione | Remediation |
| :--- | :---: | :--- | :--- |
| **gTTS** | Alta (Operativa) | Dipendenza da API non ufficiale soggetta a rate-limiting o interruzione improvvisa. | Sostituire con `pyttsx3` (offline) o API ufficiale (Google Cloud TTS / ElevenLabs). |
| **wmi** | Media | Funziona solo su Windows. Se l'app gira su Linux/Mac, crasherà all'import. | Condizionare l'import: `if os.name == 'nt': import wmi`. |
| **pygame** | Bassa | Libreria molto pesante (~20MB+) solo per riprodurre audio MP3. | Sostituire con `playsound` o `winsound` per ridurre la superficie di attacco e dimensioni. |
| **requests** | Bassa | Versione `2.32.5` è sicura, ma versioni vecchie hanno CVE. | Mantenere aggiornato (Attualmente OK). |

---

## 7. Dipendenze Outdated & Inconsistenze

### Inconsistenza PyQt6 vs Tkinter
*   **Codice:** L'applicazione principale (`desktop_app/main.py`) usa **Tkinter**.
*   **Build Script:** `admin/offusca/build_dist.py` e `admin/offusca/rthook_pyqt6.py` fanno riferimento esplicito a **PyQt6** (`import PyQt6...`, `--hidden-import PyQt6`).
*   **Requirements:** `requirements.txt` include `PyQt6` (implicito o rimosso in alcune versioni, ma presente nei log di build).
*   **Azione:** Se l'app è stata migrata a Tkinter, **PyQt6 deve essere rimosso** completamente per risparmiare ~50-100MB di spazio nell'installer e ridurre la complessità.

### Versioning
*   `requirements.txt` usa versioni molto specifiche (es. `==0.121.2`). Questo è buono per la riproducibilità ma richiede manutenzione attiva tramite strumenti come Dependabot.

---

## 8. Alternative Suggerite

| Libreria Attuale | Alternativa Suggerita | Motivo |
| :--- | :--- | :--- |
| **pygame** | `playsound` o `simpleaudio` | Pygame è un framework per giochi, eccessivo per riprodurre un feedback vocale. Risparmio: ~15MB. |
| **gTTS** | `pyttsx3` o `Edge-TTS` | gTTS è lento e richiede internet. `pyttsx3` usa le voci di sistema (SAPI5 su Windows) ed è offline/gratis. |
| **wmi** | `comtypes` o `subprocess` | `wmi` è un wrapper vecchio. `subprocess.check_output('wmic ...')` non richiede dipendenze esterne. |
| **fpdf2** | `reportlab` | `fpdf2` è buono, ma `reportlab` è lo standard industriale per PDF complessi in Python (opzionale). |

---

## 9. Lock File Analysis

*   **Python:** ❌ **MANCANTE**. Esiste solo `requirements.txt`.
    *   *Rischio:* L'installazione su una nuova macchina potrebbe scaricare versioni transitive diverse di librerie non pinnate (es. dipendenze di `fastapi`), causando bug "works on my machine".
*   **Frontend:** ✅ Presente (`package-lock.json`).

---

## 10. Raccomandazioni Prioritarie

1.  **Pulizia PyQt6:**
    *   Verificare se `PyQt6` è realmente utilizzato. Se l'app è Tkinter, rimuovere:
        *   Riferimenti in `admin/offusca/build_dist.py`.
        *   File `admin/offusca/rthook_pyqt6.py`.
        *   Eventuali import nel codice sorgente.

2.  **Freeze delle Dipendenze Python:**
    *   Generare un `requirements.lock` o usare `poetry`/`uv` per garantire build riproducibili.
    *   Comando suggerito: `pip freeze > requirements.lock`.

3.  **Sostituzione gTTS:**
    *   Per un'applicazione aziendale, l'uso di gTTS è rischioso. Implementare un fallback su `pyttsx3` se internet manca o Google blocca le richieste.

4.  **Gestione WMI:**
    *   Assicurarsi che l'import di `wmi` in `desktop_app/services/hardware_id_service.py` sia protetto da `try/except ImportError` per permettere l'esecuzione (o almeno i test) su ambienti non-Windows.

5.  **Sicurezza API Key:**
    *   Le chiavi API (Gemini, etc.) sono gestite tramite variabili d'ambiente o offuscamento (`app/core/string_obfuscation.py`). Verificare che nessuna chiave reale sia rimasta hardcodata nei file di test o nei commenti.