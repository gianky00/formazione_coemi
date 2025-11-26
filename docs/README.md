# Gestione Scadenze Certificati - Documentazione Tecnica

Questo documento fornisce una disamina tecnica approfondita del sistema di gestione dei certificati, progettato per sviluppatori e manutentori.

## Architettura del Sistema

Il progetto adotta un'architettura client-server disaccoppiata, composta da un backend API RESTful e un'applicazione desktop nativa.

-   **Backend (FastAPI):** Un server Python ad alte prestazioni che espone endpoint per tutte le operazioni CRUD, gestisce la logica di business e si interfaccia con il servizio di intelligenza artificiale.
-   **Frontend (PyQt6):** Un'applicazione desktop Windows che fornisce l'interfaccia grafica per l'interazione dell'utente, consumando le API esposte dal backend.
-   **Database (SQLite via SQLAlchemy):** Un database a file singolo, gestito tramite l'ORM SQLAlchemy, che garantisce la persistenza dei dati.
-   **Servizio AI (Google Gemini):** Sfrutta il modello `gemini-2.5-pro` per l'analisi multimodale dei documenti PDF.

---

## Dettagli Implementativi del Backend (`app/`)

Il backend è il cuore del sistema e gestisce tutta la logica applicativa.

### Gestione delle Dipendenze e Sessioni DB

La gestione delle sessioni del database è affidata al sistema di **Dependency Injection** di FastAPI.
-   La funzione `get_db` in `app/db/session.py` agisce come un "dependency provider".
-   Ogni endpoint che necessita di interagire con il database dichiara una dipendenza tramite `db: Session = Depends(get_db)`.
-   Questo pattern garantisce che ogni richiesta abbia una sessione DB dedicata, che viene chiusa correttamente al termine della richiesta, prevenendo connection leak.

### Validazione dei Dati con Pydantic

La validazione dei dati in entrata e in uscita è gestita tramite i modelli Pydantic.
-   **`CertificatoCreateSchema`**: Definisce lo schema per la creazione di un certificato, validando i dati ricevuti dal client nel body della richiesta `POST /certificati/`.
-   **`CertificatoSchema`**: Definisce lo schema per i dati in uscita. La configurazione `from_attributes = True` permette di creare istanze del modello Pydantic direttamente da oggetti SQLAlchemy, semplificando la serializzazione.

### Processo di Avvio e Seeding

All'avvio del server (tramite il `lifespan` manager), viene eseguita la funzione `seed_database`. Questa funzione popola la tabella `CorsiMaster` con un set predefinito di corsi e la loro validità in mesi. Questo assicura che il sistema abbia sempre i dati di base necessari per calcolare le scadenze, anche al primo avvio su un database vuoto.

### Logica "Get or Create"

Per evitare la duplicazione di dati, il sistema implementa una logica "Get or Create" per le entità `Dipendenti` e `CorsiMaster`.
-   Quando un certificato viene creato (`POST /certificati/`) o aggiornato (`PUT /certificati/{id}`), il sistema prima cerca nel database un record corrispondente (es. per `nome` e `cognome` del dipendente).
-   Se il record non esiste, viene creato al momento (`db.add(new_record)`) prima di procedere con la creazione dell'attestato. Questo approccio atomico mantiene l'integrità dei dati.

---

## Servizio di Analisi AI (`app/services/ai_extraction.py`)

L'analisi dei documenti avviene tramite il modello multimodale **Google Gemini 2.5 Pro** in una **singola chiamata** ottimizzata per latenza e costi.

### Processo Unificato

-   **Input:** I byte del PDF.
-   **Logica:** Un prompt ingegnerizzato ("Chain-of-Thought" implicito) guida il modello a:
    1.  Estrarre i dati anagrafici e le date.
    2.  Classificare il documento in una delle `CATEGORIE_STATICHE` seguendo regole rigide (es. distinzione tra "Nomina" e "Formazione").
-   **Output:** Un oggetto JSON con tutti i dati normalizzati.

> Per dettagli tecnici sul prompt e su come aggiungere nuove categorie, vedi [Critical System Flows](docs/CRITICAL_FLOWS.md).

---

## Dettagli Implementativi del Frontend (`desktop_app/`)

L'applicazione desktop è strutturata per essere modulare e reattiva.

### Architettura a Viste con `QStackedWidget`

-   La `MainWindow` agisce come contenitore principale e gestisce un `QStackedWidget`.
-   Ogni "schermata" dell'applicazione (`ImportView`, `DashboardView`, `ValidationView`) è un widget separato che viene aggiunto allo `QStackedWidget`.
-   La navigazione tra le viste avviene cambiando il widget corrente dello stack (`self.stacked_widget.setCurrentWidget(...)`), mantenendo il codice pulito e disaccoppiato.

### Meccanismo di Aggiornamento Dati (Segnali e Slot)

Per garantire che i dati visualizzati siano sempre aggiornati, è stato implementato un meccanismo basato su segnali e slot:
1.  Quando un'operazione in una vista modifica i dati (es. validazione di un certificato), la vista emette un segnale (es. `validation_completed`).
2.  La `MainWindow` collega questi segnali ai metodi di aggiornamento delle altre viste (es. `database_view.load_data`).
3.  Questo garantisce che le viste dipendenti vengano aggiornate automaticamente dopo ogni modifica.

---

## Ciclo di Vita di un Certificato

1.  **Caricamento e Analisi:** Un PDF viene caricato nella `ImportView`, analizzato dall'IA e i dati vengono mostrati all'utente.
2.  **Salvataggio Iniziale:** Alla conferma dell'utente, viene inviata una `POST /certificati/`. Il backend salva il certificato con `stato_validazione = ValidationStatus.AUTOMATIC`.
3.  **Validazione Manuale:** Il certificato appare nella `ValidationView`. L'utente lo controlla e clicca su "Convalida". Viene inviata una `PUT /certificati/{id}/valida`.
4.  **Stato Finale:** Il backend aggiorna lo `stato_validazione` a `ValidationStatus.MANUAL`. Da questo momento, il certificato è visibile nel `DatabaseView` principale.
5.  **Stato Certificato (Attivo/Scaduto):** Questo stato non è persistito nel database. Viene calcolato **dinamicamente** dal backend a ogni richiesta `GET /certificati/`, confrontando la `data_scadenza_calcolata` con la data corrente.

---

## Setup e Avvio (Ambiente Windows)

### Prerequisiti

-   Python 3.12 o superiore
-   Git

### Installazione

1.  **Clonare il repository:**
    ```bash
    git clone <URL_DEL_REPOSITORY>
    cd <NOME_DELLA_CARTELLA>
    ```

2.  **Creare il file `.env`:**
    Nella directory principale, creare un file `.env` e inserire la propria chiave API di Google:
    ```env
    GEMINI_API_KEY="LA_TUA_CHIAVE_API_DI_GOOGLE"
    ```

### Avvio

Fare doppio clic sul file `avvio.bat`. Lo script si occuperà di:
1.  Creare un ambiente virtuale Python (`.venv`) se non esiste.
2.  Installare le dipendenze da `requirements.txt`.
3.  Avviare il server backend FastAPI e l'applicazione desktop PyQt6.

### Testing

Per eseguire la suite di test automatizzati, eseguire il seguente comando dalla directory principale del progetto:

```bash
python -m pytest
```
