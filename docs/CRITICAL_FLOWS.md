# Flussi Critici di Sistema (System Critical Flows)

Questo documento descrive i flussi logici più complessi e sensibili dell'applicazione. È la fonte di verità per comprendere "come funziona" il sistema sotto il cofano.

## 1. Pipeline di Ingestione Dati (AI & PDF)
**Obiettivo**: Convertire PDF grezzi in record database normalizzati.

1.  **User Action**: Drag & Drop nella `ImportView`.
2.  **API Call**: `POST /upload-pdf/` (Multipart).
3.  **AI Analysis** (`app.services.ai_extraction.extract_entities_with_ai`):
    *   **Prompt**: Rigoroso ("Single Pass"), regole di business iniettate (es. "NOMINA" vs "PREPOSTO").
    *   **Model**: Google Gemini 2.5 Pro.
    *   **Resilience**: `tenacity` gestisce retries su errori 429 (Quota Exceeded) e 503.
    *   **Output**: JSON grezzo.
4.  **Backend Normalization**:
    *   **Date**: Converte formati vari (`DD-MM-YYYY`, `YYYY/MM/DD`) in standard `DD/MM/YYYY`.
    *   **Nomi**: Converte in Title Case.
5.  **Persistence** (`POST /certificati/`):
    *   Salva il file PDF in `DOCUMENTI DIPENDENTI / {Nome} / {Categoria} / {Status}`.
    *   Crea record in tabella `certificati` con `stato_validazione = AUTOMATIC`.

## 2. Risoluzione Identità e Linking (Orphan Logic)
**Obiettivo**: Associare un certificato a un dipendente univoco gestendo omonimie e dati mancanti.

1.  **Input**: Nome Dipendente (da AI) + Data Nascita (Opzionale da AI).
2.  **Matching** (`app.services.matcher.find_employee_by_name`):
    *   **Step 1 (Exact)**: Cerca corrispondenza esatta `Nome Cognome` su tabella `Dipendente`.
    *   **Step 2 (Fuzzy/Swap)**: Cerca `Cognome Nome`.
    *   **Step 3 (Omonimia)**: Se trovi >1 match:
        *   Se `data_nascita` presente nel PDF: Filtra per data.
        *   Se `data_nascita` assente: **RETURN NULL** (Ambiguità irrisolvibile).
3.  **Outcome**:
    *   **Match Univoco**: `certificato.dipendente_id` impostato.
    *   **No Match / Ambiguo**: `certificato.dipendente_id` = NULL. Salva `nome_dipendente_raw`.
    *   **Stato**: Il certificato appare in "Convalida Dati" (o "Errori Analisi" se orphan).

## 3. CSV Import & "Smart Linking"
**Obiettivo**: Importare massivamente dipendenti e "curare" i certificati orfani retroattivamente.

1.  **Upload CSV**: `POST /dipendenti/import-csv`.
2.  **Encoding Detection**: Tenta `utf-8` -> `cp1252` -> `latin1` (Robustezza per Excel).
3.  **Upsert Logic**:
    *   Itera righe. Cerca per `matricola`.
    *   Se esiste: UPDATE campi.
    *   Se nuovo: INSERT.
4.  **Orphan Healing Trigger**:
    *   Al termine dell'import, avvia scansione asincrona.
    *   Query: `SELECT * FROM certificati WHERE dipendente_id IS NULL`.
    *   Per ogni orfano: Rilancia `find_employee_by_name` usando i nuovi dati anagrafici.
    *   Se Match: Update `dipendente_id` e sposta file nella cartella corretta.

## 4. Macchina a Stati del Certificato (Status Engine)
**Obiettivo**: Calcolare dinamicamente lo stato "Business" di un certificato.
*File*: `app/services/certificate_logic.py`.

| Stato Calcolato | Logica Temporale | Condizioni Extra |
| :--- | :--- | :--- |
| **SCADUTO** | `data_scadenza < Oggi` | Nessun certificato più recente esiste per (Dipendente, Categoria). |
| **RINNOVATO** | `data_scadenza < Oggi` | Esiste un certificato con `data_rilascio` successiva per lo stesso (Dipendente, Categoria). |
| **IN SCADENZA** | `Oggi <= data_scadenza <= Oggi + Threshold` | Thresholds: 30gg (Visite), 60gg (Corsi). |
| **ATTIVO** | `data_scadenza > Oggi + Threshold` | - |

*   **Nota**: I certificati orfani non possono mai essere "RINNOVATI" (manca il link al dipendente per il confronto).

## 5. License Auto-Update Flow
**Obiettivo**: Aggiornare le licenze da remoto senza intervento utente.
*Vedi [System Design Report](SYSTEM_DESIGN_REPORT.md) per dettagli crypto.*

1.  **Trigger**: `launcher.py` rileva licenza Scaduta/Mancante/Tampered.
2.  **Config Fetch**: Recupera `HardwareID` e Token GitHub (via API backend o Config Recovery).
3.  **Manifest Check**: Scarica `manifest.json` da Repo GitHub (`/licenses/{HWID}/`).
4.  **Diff Check**: Confronta SHA256 dei file locali (`pyarmor.rkey`, `config.dat`) con il manifest.
5.  **Atomic Update**:
    *   Scarica file in `TempDir`.
    *   Verifica Checksum.
    *   `shutil.move` sovrascrive file in `%LOCALAPPDATA%`.
6.  **Restart**: Riavvio forzato applicazione.

## 6. Secure Boot & Time Validation
**Obiettivo**: Prevenire manomissioni dell'orologio e garantire integrità.

1.  **Gatekeeper**: `launcher.py` parte prima della GUI.
2.  **Time Check** (`time_service.py`):
    *   **Online**: Query NTP (`pool.ntp.org`). Tolleranza 5 min.
    *   **Offline**: Check `secure_time.dat`.
        *   Anti-Rollback (`SysTime < LastExec`).
        *   Buffer (`SysTime > LastOnline + 3gg`).
3.  **Environment Check**:
    *   Verifica esistenza Database.
    *   Verifica integrità file critici.
    *   Se errori -> Modalità Recovery (Dialog "Sfoglia/Crea DB").

## 7. Notification System Logic
**Obiettivo**: Inviare report PDF via email.

1.  **Trigger**: Schedule (08:00) o Manuale.
2.  **Generazione PDF**:
    *   `fpdf2` crea PDF in RAM (ByteStream).
    *   Tabelle: "In Scadenza (Corsi)", "In Scadenza (Visite)", "Scaduti".
3.  **Invio SMTP**:
    *   Tenta SSL (465). Fallback TLS (587). Fallback Plain (25).
    *   Allega PDF.

## 8. Lyra RAG & Voice Pipeline
**Obiettivo**: Chatbot contestuale con voce.

1.  **Query**: Utente scrive in chat.
2.  **RAG**: Backend recupera contesto da DB (Statistiche) e Docs Markdown (`docs/*.md`).
3.  **Generation**: Gemini genera risposta impersonando "Lyra" (Profilo in `LYRA_PROFILE.md`).
4.  **TTS (Opzionale)**: Invia testo a `edge-tts`. Riceve MP3. Frontend riproduce audio.
