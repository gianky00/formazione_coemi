# Gestione Scadenze Certificati con IA - Documentazione Tecnica

Questo progetto è un sistema integrato per la gestione delle scadenze dei certificati di formazione sulla sicurezza. Sfrutta un'architettura client-server con un frontend desktop, un backend API e servizi di intelligenza artificiale per l'analisi automatica dei documenti.

## Architettura Generale

Il sistema è composto da tre componenti principali:

*   **Backend API (FastAPI):** Un'applicazione Python basata su FastAPI che gestisce la logica di business, le interazioni con il database e la comunicazione con i servizi di IA.
*   **Frontend Desktop (PyQt6):** Un'applicazione desktop multipiattaforma costruita con PyQt6 che fornisce l'interfaccia utente per l'interazione con il sistema.
*   **Servizio di Intelligenza Artificiale (Google Gemini):** Utilizza il modello multimodale di Google Gemini per analizzare direttamente i file PDF e estrarre le informazioni pertinenti.

### Stack Tecnologico

| Componente | Tecnologia | Descrizione |
| --- | --- | --- |
| **Backend** | Python 3.12, FastAPI, Uvicorn | Gestisce le richieste API, la logica di business e il server web. |
| **Frontend** | Python 3.12, PyQt6 | Fornisce l'interfaccia utente grafica. |
| **Database** | SQLAlchemy, SQLite | ORM per l'interazione con il database e database a file singolo. |
| **IA** | Google Gemini (`gemini-2.5-pro`) | Estrazione di entità e classificazione da documenti PDF. |
| **Configurazione**| Pydantic | Gestione della configurazione tramite variabili d'ambiente. |

## Flusso di Lavoro dei Dati

Il flusso di lavoro principale, dalla ricezione di un certificato PDF alla sua archiviazione e visualizzazione, è il seguente:

1.  **Caricamento del PDF:** L'utente seleziona un file PDF tramite la `ImportView` nell'applicazione desktop.
2.  **Analisi con IA:** L'applicazione invia i byte del PDF all'endpoint `/upload-pdf/` del backend. Il backend, a sua volta, invia i byte a Google Gemini per l'analisi.
3.  **Estrazione in Due Fasi:**
    *   **Fase 1 (Estrazione Dati):** Gemini estrae le informazioni di base: `nome`, `corso`, e `data_rilascio`.
    *   **Fase 2 (Classificazione):** Gemini classifica il `corso` estratto in una delle categorie predefinite (es. `ANTINCENDIO`, `PRIMO SOCCORSO`, ecc.). Se nessuna categoria corrisponde, viene assegnata la categoria `ALTRO`.
4.  **Calcolo della Scadenza:** Il backend utilizza la `categoria` restituita dall'IA per cercare la validità in mesi nel database (`CorsiMaster`) e calcolare la `data_scadenza`.
5.  **Creazione del Certificato non Validato:** I dati estratti e calcolati vengono salvati nel database con uno stato di validazione `AUTOMATIC`.
6.  **Validazione Manuale:** L'utente visualizza i certificati non validati nella `ValidationView` e, dopo averne verificato la correttezza, li valida. Questa azione imposta lo stato a `MANUAL`.
7.  **Visualizzazione nel Dashboard:** I certificati con stato `MANUAL` vengono visualizzati nel `DashboardView`, dove possono essere modificati o eliminati.

## Configurazione dell'Ambiente

Seguire questi passaggi per configurare l'ambiente di sviluppo.

### Prerequisiti

*   Python 3.12 o superiore
*   Git
*   (Linux) `libxcb-cursor0`: Dipendenza di sistema per PyQt6. Installare con `sudo apt-get update && sudo apt-get install -y libxcb-cursor0`.

### Installazione

1.  **Clonare il repository:**
    ```bash
    git clone <URL_DEL_REPOSITORY>
    cd <NOME_DELLA_CARTELLA>
    ```

2.  **Creare il file `.env`:**
    Nella directory principale del progetto, creare un file `.env` e aggiungere la seguente variabile:
    ```env
    GEMINI_API_KEY="LA_TUA_CHIAVE_API_DI_GOOGLE"
    ```

3.  **Installare le dipendenze Python:**
    ```bash
    pip install -r requirements.txt
    ```

## Avvio dell'Applicazione

I comandi per avviare l'applicazione variano a seconda del sistema operativo.

### Windows

Eseguire il file `run.bat`. Questo script automatizza i seguenti passaggi:
1.  Avvia il server backend FastAPI in background.
2.  Lancia l'applicazione desktop PyQt6.

### Linux

1.  **Avviare il backend FastAPI:**
    ```bash
    PYTHONPATH=. python3 app/main.py &
    ```
2.  **Avviare il frontend PyQt6:**
    ```bash
    PYTHONPATH=. python3 desktop_app/main_window.py
    ```

## Endpoint API

Di seguito è riportata una descrizione dettagliata degli endpoint API disponibili.

| Metodo | URL | Descrizione |
| --- | --- | --- |
| `POST` | `/upload-pdf/` | Carica un file PDF, lo analizza con Gemini, calcola la data di scadenza e restituisce i dati estratti. |
| `GET` | `/certificati/` | Recupera un elenco di certificati. Può essere filtrato per stato di validazione con `?validated=true` o `?validated=false`. |
| `POST`| `/certificati/` | Crea un nuovo certificato nel database con stato `AUTOMATIC`. Se il dipendente o il corso non esistono, li crea. |
| `PUT` | `/certificati/{id}` | Aggiorna un certificato esistente. Richiede `nome`, `corso`, `categoria` e `data_rilascio`. |
| `DELETE`| `/certificati/{id}`| Elimina un certificato specifico. |
| `PUT` | `/certificati/{id}/valida`| Imposta lo stato di validazione di un certificato su `MANUAL`. |
| `GET` | `/corsi` | Restituisce un elenco di tutti i corsi master presenti nel database. |
| `GET` | `/health` | Endpoint di health check per verificare che il server sia in esecuzione. |
| `GET` | `/` | Endpoint di root che restituisce un messaggio di benvenuto. |

## Struttura del Progetto

```
.
├── app/                  # Codice del backend FastAPI
│   ├── api/              # Definizione degli endpoint API (main.py)
│   ├── core/             # Configurazione dell'applicazione (config.py)
│   ├── db/               # Modelli SQLAlchemy e gestione della sessione del database
│   ├── services/         # Logica di integrazione con servizi esterni (ai_extraction.py)
│   └── main.py           # Punto di ingresso dell'applicazione FastAPI
├── desktop_app/          # Codice del frontend PyQt6
│   ├── import_view.py    # Vista per il caricamento dei PDF
│   ├── dashboard_view.py # Vista per la visualizzazione dei certificati validati
│   ├── validation_view.py# Vista per la validazione dei certificati estratti dall'IA
│   ├── config_view.py    # Vista per la configurazione (attualmente non implementata)
│   └── main_window.py    # Finestra principale dell'applicazione
├── .env                  # File di configurazione delle variabili d'ambiente (da creare)
├── readme.md             # Questo file
├── requirements.txt      # Dipendenze Python
└── run.bat               # Script di avvio per Windows
```