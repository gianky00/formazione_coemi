Ecco il file `PROJECT_CONTEXT.md` generato basandosi sull'analisi approfondita del codice sorgente fornito.

***

# PROJECT_CONTEXT.md - CONTESTO PROGETTO ESAUSTIVO

## 1. Executive Summary

**Intelleo** è una piattaforma software desktop avanzata (Windows) progettata per la gestione automatizzata della **sicurezza sul lavoro** e della formazione aziendale. Il sistema funge da "Assistente Intelligente" che centralizza la gestione dei dipendenti, dei corsi di formazione e delle visite mediche.

Il core value risiede nell'uso dell'**Intelligenza Artificiale (Google Gemini)** per automatizzare l'estrazione dati dai certificati PDF scansionati, riducendo drasticamente il data entry manuale. L'applicazione adotta un'architettura **Local-First sicura**: il database è crittografato su disco e decifrato solo in RAM, garantendo la privacy dei dati sensibili. Il sistema include un assistente RAG (Retrieval-Augmented Generation) chiamato "Lyra" per interrogare i dati in linguaggio naturale.

## 2. Problema e Soluzione

### Pain Points (Il Problema)
*   **Data Entry Manuale:** L'inserimento manuale di dati da centinaia di attestati PDF è lento ed incline a errori umani (date, nomi, tipologie corsi).
*   **Scadenze Mancate:** La gestione tramite Excel porta spesso a scadenze non monitorate, rischiando sanzioni o mancata conformità.
*   **Dispersione Documentale:** I file PDF sono spesso sparsi in cartelle di rete disorganizzate senza un collegamento diretto al record del dipendente.
*   **Sicurezza Dati:** I dati sensibili dei dipendenti sono spesso conservati in chiaro.

### Value Proposition (La Soluzione)
*   **Automazione AI:** Drag & drop di PDF -> L'AI estrae Nome, Corso, Data Rilascio e calcola la Scadenza.
*   **Validazione Human-in-the-loop:** Un'interfaccia dedicata permette di validare i dati estratti dall'AI prima di salvarli nel DB ufficiale.
*   **Organizzazione Automatica:** Il software rinomina e sposta automaticamente i file PDF in una struttura di cartelle standardizzata (`Cognome Nome (Matricola)/Categoria/Stato`).
*   **Sicurezza Militare:** Database SQLite crittografato con Fernet (AES), accessibile solo tramite l'applicazione (decifratura in-memory).
*   **Scadenzario Proattivo:** Notifiche email automatiche e visualizzazione Gantt delle scadenze imminenti.

## 3. Utenti Target (Personas)

| Persona | Ruolo | Obiettivi Principali | Funzionalità Chiave |
| :--- | :--- | :--- | :--- |
| **HSE Manager** | Responsabile Sicurezza | Monitorare la conformità aziendale, evitare sanzioni, pianificare la formazione. | Dashboard, Scadenzario, Reportistica PDF, Chat con Lyra. |
| **HR Admin** | Amministrazione | Inserire nuovi dipendenti, caricare attestati, gestire le anagrafiche. | Importazione AI, Import CSV, Gestione Dipendenti, Validazione. |
| **IT Admin** | Supporto Tecnico | Configurare il sistema, gestire i backup e la sicurezza. | Configurazione (SMTP, Percorsi), Log di Audit, Manutenzione DB. |

## 4. Funzionalità Principali

### A. Importazione e Analisi AI
*   **Descrizione:** Upload di PDF (singoli o cartelle). L'AI (Gemini 2.5 Pro) analizza il contenuto OCR/Testo.
*   **Logica:** `app/services/ai_extraction.py` invia il contenuto a Google Gemini con un prompt specifico per categorizzare il documento (es. "ANTINCENDIO", "PLE", "VISITA MEDICA").
*   **Output:** JSON strutturato con dati normalizzati.
*   **Gestione Errori:** I file non riconosciuti o con dati parziali vengono marcati come "Orfani" o "Errori Analisi".

### B. Gestione Database Sicura (In-Memory Encryption)
*   **Descrizione:** Il database `database_documenti.db` è cifrato su disco.
*   **Tecnica:** `app/core/db_security.py` carica il file cifrato, lo decifra in un buffer di memoria e usa `sqlite3.connect(':memory:')` con `deserialize`. Al salvataggio, serializza la memoria, cifra e scrive su disco.
*   **Locking:** Un sistema di `LockManager` basato su file system impedisce l'apertura concorrente dello stesso DB da più istanze, forzando la modalità "Sola Lettura".

### C. Scadenzario e Notifiche
*   **Descrizione:** Monitoraggio scadenze con soglie configurabili (default 60gg per corsi, 30gg per visite).
*   **Automazione:** `app/services/notification_service.py` esegue un job (APScheduler) o trigger manuale per inviare report PDF via email (SMTP) con le scadenze imminenti.

### D. Chatbot "Lyra" (RAG)
*   **Descrizione:** Assistente virtuale integrato nella GUI.
*   **Funzionamento:** `app/services/chat_service.py` costruisce un contesto testuale con statistiche, scadenze e dati orfani, e lo invia a Gemini Flash per permettere all'utente di fare domande in linguaggio naturale (es. "Chi ha il corso antincendio scaduto?").

### E. Sistema di Licenza
*   **Descrizione:** Protezione software legata all'Hardware ID della macchina.
*   **Tecnica:** `desktop_app/services/hardware_id_service.py` calcola un ID univoco (Seriale Disco o MAC). Il file `config.dat` contiene la scadenza cifrata.

## 5. Roadmap e Backlog

### Stato Attuale (v1.0.0)
*   [x] Migrazione Backend a FastAPI (architettura locale client-server).
*   [x] Interfaccia Desktop migrata a **Tkinter** (il codice `desktop_app/views` usa Tkinter, anche se ci sono tracce di build PyQt).
*   [x] Compilazione con **Nuitka** per performance e offuscamento.

### TODO / Miglioramenti Tecnici (Dal Codice)
1.  **Discrepanza UI Framework:** Gli script di build (`build_nuitka.py`) includono plugin per `PyQt6` e ci sono test/mock per Qt, ma il codice dell'app (`desktop_app/main.py`, `views/*.py`) usa esplicitamente `tkinter`.
    *   *Azione:* Rimuovere le dipendenze PyQt6 dal processo di build per ridurre la dimensione dell'eseguibile se non utilizzate.
2.  **Recursion Limit:** In `launcher.py` c'è `sys.setrecursionlimit(5000)`. Questo è un "code smell" che indica probabili ricorsioni profonde non ottimizzate (forse nel parsing di cartelle o nell'interfaccia grafica).
3.  **Sicurezza API Key:** Le chiavi API (Gemini, GitHub) sono offuscate (`obf:...`) ma presenti nel codice.
    *   *Miglioramento:* Spostare le chiavi sensibili in un vault esterno o criptarle con chiave utente.
4.  **Gestione Concorrenza:** Il sistema usa un lock file su disco. Se il processo crasha male, il lock potrebbe rimanere (anche se c'è logica di "stale lock" basata su PID, potrebbe fallire in rete).

## 6. Glossario Completo

| Termine | Definizione | Contesto |
| :--- | :--- | :--- |
| **Orfano** | Un certificato analizzato dall'AI ma non collegato a nessun dipendente (es. matricola non trovata o nome non corrispondente). | Database / Validazione |
| **Upsert** | Logica di importazione CSV: Aggiorna se esiste (basandosi su Matricola), Crea se nuovo. | Importazione Dipendenti |
| **Hardware ID (HWID)** | Impronta digitale univoca del PC (Seriale Disco C:) usata per il DRM. | Licensing |
| **In-Memory DB** | Il database SQLite risiede interamente nella RAM durante l'esecuzione per velocità e sicurezza (decifratura volante). | Core Architecture |
| **Lyra** | Nome della persona dell'assistente AI. | Chatbot |
| **RAG** | Retrieval-Augmented Generation. Tecnica usata da Lyra per rispondere basandosi sui dati del DB. | AI Service |
| **Gantt** | Visualizzazione temporale a barre delle validità dei certificati. | Scadenzario |
| **Lock File** | File `.database_documenti.db.lock` creato per gestire l'accesso esclusivo al DB. | Concorrenza |

## 7. Integrazioni Esterne

### API
*   **Google Gemini (Generative AI):**
    *   Modello Analisi: `gemini-2.5-pro` (per estrazione dati PDF).
    *   Modello Chat: `gemini-2.5-flash` (per Lyra).
*   **GitHub API:** Utilizzata per l'auto-aggiornamento delle licenze (`desktop_app/services/license_updater_service.py`).
*   **ElevenLabs:** Configurata in `config.py` per sintesi vocale (Voice Assistant), anche se `voice_service.py` sembra usare `gTTS` e `pygame` come fallback/implementazione attuale.

### Database & Storage
*   **SQLite:** Database principale, cifrato custom.
*   **File System:** Archiviazione fisica dei PDF organizzata gerarchicamente.

## 8. Metriche di Successo (KPI)

1.  **Tasso di Riconoscimento AI:** % di documenti importati senza finire in "Analisi Errori" o richiedere correzioni manuali massicce.
2.  **Tempo di Avvio:** Target < 5 secondi (verificato da `admin/tools/benchmark_builds.py`).
3.  **Compliance Aziendale:** % di certificati "Attivi" vs "Scaduti" (visualizzabile in Dashboard).
4.  **Stabilità:** Numero di crash report generati in `CRITICAL FLOWS TEST`.

## 9. Rischi e Mitigazioni

| Rischio | Probabilità | Impatto | Mitigazione Implementata |
| :--- | :--- | :--- | :--- |
| **Perdita Chiave Crittografica** | Bassa | Catastrofico | La chiave Fernet è offuscata nel codice ma statica. Backup regolari del DB (non cifrati o cifrati diversamente) sono essenziali. |
| **Corruzione Database** | Media | Alto | Il sistema In-Memory riduce le scritture su disco, ma un crash durante il `save_to_disk` è critico. Il sistema fa backup a rotazione (`.bak`). |
| **Allucinazioni AI** | Media | Medio | I dati estratti vanno in un'area di "Validazione" (Staging) prima di diventare ufficiali. L'utente deve confermare. |
| **Blocco File (Locking)** | Alta | Basso | Logica di `stale lock recovery` in `db_security.py` che controlla se il processo PID nel lock file è ancora vivo. |

## 10. Contatti e Risorse

*   **Repository:** `https://github.com/gianky00/formazione_coemi` (Dedotto da script admin).
*   **Documentazione Tecnica:** Cartella `docs/` nel progetto.
*   **Frontend Guide:** Progetto React in `guide_frontend/`.
*   **Issue Tracker:** GitHub Issues (privato).

---

### Esempi di Codice Pratici per Agenti AI

**1. Come decifrare il Database (Python):**
```python
from app.core.db_security import DBSecurityManager
# Inizializza il manager (trova automaticamente il percorso in appdata)
manager = DBSecurityManager()
# Carica e decifra in memoria
manager.load_memory_db()
# Ottieni connessione SQLite standard
conn = manager.get_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM dipendenti")
```

**2. Come lanciare l'analisi AI su un PDF:**
```python
from app.services.ai_extraction import extract_entities_with_ai

with open("certificato.pdf", "rb") as f:
    pdf_bytes = f.read()

# Ritorna dict: {'nome': '...', 'corso': '...', 'data_scadenza': '...'}
dati = extract_entities_with_ai(pdf_bytes)
```

**3. Struttura Cartelle Documenti:**
La path resolution è critica. Usare sempre `app.services.document_locator`.
```text
%LOCALAPPDATA%/Intelleo/
├── database_documenti.db (Cifrato)
├── .database_documenti.db.lock
├── DOCUMENTI DIPENDENTI/
│   ├── ROSSI MARIO (123)/
│   │   ├── ANTINCENDIO/
│   │   │   ├── ATTIVO/
│   │   │   │   └── ROSSI MARIO (123) - ANTINCENDIO - 31_12_2025.pdf
│   │   │   └── STORICO/
│   │   │       └── ...
```