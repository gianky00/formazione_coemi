# Manuale Tecnico per Sviluppatori - Gestione Scadenziario Certificati IA

Questo documento fornisce un'analisi tecnica approfondita del progetto, destinata agli sviluppatori. Spiega le decisioni architetturali, le dinamiche interne del codice e le best practice adottate.

## 1. Filosofia e Decisioni Architetturali

La progettazione di questo sistema si basa su alcuni principi chiave: robustezza, manutenibilità e separazione delle competenze.

-   **Architettura Client-Server:** La scelta di un'architettura disaccoppiata con un backend **FastAPI** e un frontend **PyQt6** è strategica. Permette di:
    -   **Separare la Logica di Business dall'UI:** Il backend gestisce in modo centralizzato i dati e l'integrazione con l'IA, mentre il frontend si occupa esclusivamente della presentazione e dell'interazione con l'utente.
    -   **Scalabilità e Flessibilità:** In futuro, sarà possibile sviluppare nuovi client (es. un'app web) senza modificare il backend.

-   **Perché FastAPI?** È stato scelto per le sue performance elevate e per la sua integrazione nativa con **Pydantic**, che permette di definire "schemi" di dati chiari e di ottenere una validazione automatica e robusta degli input API, un punto cruciale per la stabilità del sistema.

-   **Perché PyQt6?** Offre un'esperienza utente nativa e reattiva su Windows. La sua natura event-driven si integra bene con un backend RESTful.

## 2. Approfondimento sul Backend (`app/`)

### 2.1. Validazione Robusta con Pydantic (`app/api/main.py`)

La stabilità dell'API si fonda su una rigorosa validazione a livello di modello, implementata tramite i `field_validator` di Pydantic V2.

-   **Prevenzione degli Errori 500:** La validazione intercetta i dati non conformi *prima* che raggiungano la logica di business. Questo trasforma potenziali `ValueError` (che causerebbero un 500 Internal Server Error) in risposte `422 Unprocessable Entity` con messaggi di errore chiari per il client.
-   **Gestione Flessibile della `data_scadenza`:** Il validatore per `data_scadenza` è un esempio di design difensivo.
    ```python
    @field_validator('data_scadenza')
    def validate_data_scadenza_format(cls, v):
        if v is None or not v.strip() or v.strip().lower() == 'none':
            return None
        # ... conversione a data
    ```
    Questa logica accetta non solo `null` (JSON), ma anche stringhe vuote (`""`) o la stringa letterale `"none"`. Questo rende l'API resiliente a diverse rappresentazioni di un valore nullo inviate da client diversi o in seguito a modifiche accidentali.

### 2.2. Efficienza del Database con SQLAlchemy

-   **Prevenzione delle N+1 Query:** Per evitare problemi di performance, l'endpoint `GET /certificati/` utilizza l'eager loading di SQLAlchemy.
    ```python
    query = db.query(Certificato).options(
        selectinload(Certificato.dipendente),
        selectinload(Certificato.corso)
    )
    ```
    `selectinload` istruisce SQLAlchemy a caricare le relazioni (`dipendente`, `corso`) con query aggiuntive ma efficienti (una per ogni relazione), piuttosto che una query per ogni certificato, prevenendo il classico problema delle "N+1 query".

-   **Pattern "Get or Create":** Durante la creazione e l'aggiornamento di un certificato, il sistema non fallisce se il dipendente o il corso non esistono. Invece, li crea al volo. Questa logica:
    -   Migliora l'esperienza utente, che non deve pre-caricare entità correlate.
    -   Garantisce l'integrità referenziale, poiché un certificato non può essere associato a un ID inesistente.

### 2.3. Integrazione del Servizio AI (`app/services/ai_extraction.py`)

L'analisi dei PDF è un processo a due fasi per massimizzare l'accuratezza:

1.  **Estrazione delle Entità:** Una prima chiamata al modello Gemini Pro analizza i byte del PDF per estrarre le entità principali (nome, corso, date).
2.  **Classificazione della Categoria:** Una seconda chiamata, più mirata, classifica il `nome_corso` estratto in una delle categorie predefinite (`CorsiMaster`). Questo approccio è stato scelto perché la classificazione richiede un "ragionamento" diverso rispetto alla semplice estrazione, e separare i compiti migliora l'affidabilità del risultato finale.

## 3. Approfondimento sul Frontend (`desktop_app/`)

### 3.1. Integrità dei Dati alla Fonte (`desktop_app/edit_dialog.py`)

Il problema persistente degli errori 422 è stato risolto non sul backend, ma alla sua origine: il frontend.

-   **Da `QInputDialog` a `EditCertificatoDialog`:** La catena di `QInputDialog` era fragile perché permetteva l'inserimento di qualsiasi testo in qualsiasi campo.
-   **La Soluzione Strategica:** Il nuovo `EditCertificatoDialog` utilizza widget specifici:
    -   `QLineEdit` per il testo.
    -   `QDateEdit` per le date. Questo widget **costringe** l'utente a inserire una data valida, eliminando alla radice la possibilità di inviare testo errato (es. "LAVORI IN QUOTA") in un campo data.
    -   Una `QCheckBox` per la `data_scadenza` permette di gestire il valore opzionale in modo chiaro e di inviare `null` al backend quando deselezionata.

## 4. Strategia di Testing Avanzata (`tests/`)

La suite di test è progettata per essere veloce, deterministica e completa.

-   **Database In-Memory (`tests/conftest.py`):** I test non usano il database di produzione, ma un database SQLite in-memory. L'uso di `StaticPool` garantisce una connessione singola e stabile per l'intera sessione di test, prevenendo errori di "table not found".
-   **Mocking del Servizio AI (`tests/app/api/test_main.py`):** Le chiamate al servizio AI Gemini sono mockate con `pytest-mock`.
    ```python
    mocker.patch(
        "app.api.main.ai_extraction.extract_entities_with_ai",
        return_value=mocked_extracted_data
    )
    ```
    Questo rende i test:
    -   **Veloci:** Non vengono effettuate chiamate di rete.
    -   **Deterministi:** La risposta dell'AI è controllata e prevedibile.
    -   **Economici:** Non vengono consumati token API.
-   **Copertura con Parametrizzazione:** Per testare in modo efficiente la validazione degli input, si usa `pytest.mark.parametrize`.
    ```python
    @pytest.mark.parametrize("input_scadenza, expected_db_value, ...", [
        ("15/12/2030", date(2030, 12, 15), ...),
        (None, None, ...),
        ("", None, ...),
        ("None", None, ...),
    ])
    ```
    Questo approccio permette di testare decine di scenari di input con un'unica funzione di test, garantendo una copertura completa della logica di validazione.
