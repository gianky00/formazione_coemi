# Gestione Scadenziario Certificati IA

## 1. Panoramica del Progetto

Questo progetto è un sistema software per la gestione delle scadenze dei certificati di formazione sulla sicurezza sul lavoro. L'applicazione è progettata per automatizzare il processo di estrazione dei dati dai certificati in formato PDF e per fornire un'interfaccia di gestione per monitorare, validare e aggiornare le scadenze.

Il cuore del sistema è un modello di IA multimodale (Google Gemini Pro) che analizza direttamente i file PDF, estraendo entità chiave come nome del dipendente, nome del corso, data di rilascio e categoria. Questi dati vengono poi archiviati in un database per la gestione e il monitoraggio.

## 2. Architettura

Il sistema segue un'architettura client-server:

-   **Backend:** Un'API RESTful sviluppata con **FastAPI**. Gestisce tutta la logica di business, l'interazione con il database, l'integrazione con il servizio di IA e l'esposizione dei dati tramite endpoint HTTP.
-   **Frontend:** Un'applicazione desktop sviluppata con **PyQt6**. Fornisce un'interfaccia utente grafica (GUI) per interagire con il backend, consentendo agli utenti di caricare PDF, visualizzare, validare e modificare i certificati.

## 3. Stack Tecnologico

-   **Linguaggio:** Python 3.12
-   **Backend:**
    -   **Framework API:** FastAPI
    -   **ORM:** SQLAlchemy
    -   **Validazione Dati:** Pydantic V2
    -   **Server ASGI:** Uvicorn
-   **Frontend:**
    -   **Framework GUI:** PyQt6
-   **Database:**
    -   **Produzione/Default:** SQLite (per semplicità di setup)
    -   **Test:** SQLite in-memory
-   **Servizio AI:**
    -   **Modello:** Google Gemini Pro (multimodale)
-   **Testing:**
    -   **Framework:** Pytest
    -   **Librerie:** `pytest-mock`, `httpx` (per test di integrazione API)

## 4. Setup e Installazione

L'ambiente di sviluppo e l'applicazione sono pensati per essere eseguiti su **Windows**.

### Prerequisiti

-   Python 3.12 installato e aggiunto al PATH di sistema.
-   Una chiave API per Google Gemini, che deve essere impostata come variabile d'ambiente `GEMINI_API_KEY`.

### Installazione

1.  Clonare il repository.
2.  Eseguire lo script `run.bat` dalla root del progetto. Questo script automatizza l'intero processo:
    1.  Crea un ambiente virtuale Python nella directory del progetto.
    2.  Attiva l'ambiente virtuale.
    3.  Installa tutte le dipendenze Python da `requirements.txt`.
    4.  Avvia il server backend FastAPI in background.
    5.  Avvia l'applicazione desktop PyQt6.

## 5. Utilizzo e Script

### `run.bat`

Questo è lo script principale per avviare l'applicazione. Esegue tutti i passaggi necessari, dalla creazione dell'ambiente all'avvio dei servizi.

```bash
run.bat
```

### `restart.bat`

Questo script è stato creato per fornire un modo sicuro di "resettare" l'ambiente di sviluppo. È utile in caso di problemi con le dipendenze o per iniziare da uno stato pulito.

**ATTENZIONE:** Questo script terminerà forzatamente **tutti** i processi `python.exe` in esecuzione sulla macchina.

Lo script esegue le seguenti azioni:
1.  Chiede conferma all'utente.
2.  Termina tutti i processi Python.
3.  Rimuove le cartelle dell'ambiente virtuale (`Lib`, `Scripts`, `Include`) e il file `pyvenv.cfg`.
4.  Esegue `run.bat` per ricreare l'ambiente e riavviare l'applicazione.

```bash
restart.bat
```

## 6. Testing

La suite di test è costruita con Pytest e si trova nella directory `/tests`. I test sono strutturati per rispecchiare la struttura dell'applicazione.

Per eseguire l'intera suite di test, assicurarsi che le dipendenze di sviluppo siano installate (incluse in `requirements.txt`) e lanciare il seguente comando dalla root del progetto:

```bash
python -m pytest
```

I test utilizzano un database SQLite in-memory per garantire l'isolamento e la velocità di esecuzione.

## 7. Struttura del Progetto

```
.
├── app/                  # Codice sorgente del backend FastAPI
│   ├── api/              # Modelli Pydantic e endpoint API
│   ├── core/             # Configurazione dell'applicazione
│   ├── db/               # Modelli SQLAlchemy e gestione sessione DB
│   ├── services/         # Logica di business (IA, calcolo scadenze)
│   └── main.py           # Entrypoint dell'applicazione backend
│
├── desktop_app/          # Codice sorgente del frontend PyQt6
│   ├── dashboard_view.py # Vista principale di gestione
│   ├── edit_dialog.py    # Dialogo di modifica certificati
│   └── main_window.py    # Finestra principale dell'applicazione
│
├── tests/                # Suite di test
│   └── app/              # Test per il backend
│
├── requirements.txt      # Dipendenze Python
├── run.bat               # Script di avvio
└── restart.bat           # Script di pulizia e riavvio
```

## 8. Documentazione API (Sintetica)

-   `POST /upload-pdf/`: Carica un file PDF. L'API estrae i dati tramite IA e li restituisce in formato JSON.
-   `POST /certificati/`: Crea un nuovo certificato nel database. Richiede un corpo JSON con i dati del certificato.
-   `GET /certificati/`: Restituisce un elenco di certificati. Può essere filtrato con il query parameter `?validated=true|false`.
-   `PUT /certificati/{id}`: Aggiorna un certificato esistente. Richiede un corpo JSON con i dati aggiornati.
-   `PUT /certificati/{id}/valida`: Imposta lo stato di un certificato su `MANUAL`.
-   `DELETE /certificati/{id}`: Elimina un certificato.
