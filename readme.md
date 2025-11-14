# Gestione Scadenze Certificati con IA

Questo progetto è un'applicazione desktop per la gestione delle scadenze dei certificati di formazione sulla sicurezza, potenziata da un backend FastAPI che utilizza l'intelligenza artificiale di Google Gemini per estrarre informazioni direttamente dai file PDF.

## Stack Tecnologico

*   **Backend:** FastAPI, Python 3.12
*   **Frontend:** PyQt6
*   **Database:** SQLAlchemy con SQLite
*   **Intelligenza Artificiale:** Google Gemini
*   **Librerie Principali:** pydantic, uvicorn

## Istruzioni di Setup

Segui questi passaggi per installare e avviare il progetto su un nuovo computer.

### Prerequisiti

*   Python 3.12 o superiore
*   Git

### Installazione

1.  **Clona il repository:**
    ```bash
    git clone <URL_DEL_TUO_REPOSITORY>
    cd <NOME_DELLA_CARTELLA>
    ```

2.  **Crea il file `.env`:**
    Nella cartella principale del progetto, crea un file chiamato `.env` e aggiungi le seguenti chiavi:
    ```env
    GEMINI_API_KEY="LA_TUA_CHIAVE_API_QUI"
    GEMINI_MODEL_NAME="gemini-1.5-pro-latest"
    ```
    Sostituisci `"LA_TUA_CHIAVE_API_QUI"` con la tua chiave API di Google Gemini.

3.  **Esegui `run.bat`:**
    Fai doppio clic sul file `run.bat` (su Windows). Questo script si occuperà di:
    *   Creare un ambiente virtuale Python (`.venv`).
    *   Installare tutte le dipendenze da `requirements.txt`.
    *   Avviare il backend FastAPI.
    *   Lanciare l'applicazione desktop PyQt6.

## Struttura del Progetto

*   `app/`: Contiene tutto il codice del backend FastAPI.
    *   `api/`: Definisce gli endpoint dell'API.
    *   `core/`: Gestisce la configurazione (es. caricamento delle variabili d'ambiente).
    *   `db/`: Contiene i modelli SQLAlchemy e la configurazione del database.
    *   `services/`: Include la logica per l'integrazione con l'IA di Gemini.
*   `desktop_app/`: Contiene il codice sorgente per l'applicazione desktop PyQt6.
*   `uploads/`: Cartella (creata dinamicamente) dove potrebbero essere salvati temporaneamente i file caricati.
*   `database.db`: Il file del database SQLite.

## Endpoint API Principali

*   `POST /upload-pdf/`: Carica un file PDF, lo analizza con Gemini per estrarre i dati del certificato (nome, corso, date) e restituisce un'anteprima.
*   `POST /certificati/`: Salva i dati di un nuovo certificato nel database. Se il dipendente o il corso non esistono, li crea automaticamente.
*   `GET /certificati/`: Recupera un elenco di tutti i certificati salvati. Può essere filtrato per stato di validazione (`?validated=true` o `?validated=false`).
*   `PUT /certificati/{id}`: Aggiorna i dati di un certificato esistente.
*   `DELETE /certificati/{id}`: Elimina un certificato.
*   `PUT /certificati/{id}/valida`: Imposta lo stato di un certificato come "validato manualmente".
