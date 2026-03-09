# 🛠 Piano di Refactoring e Modularizzazione: Intelleo

Stato: **PIANIFICAZIONE COMPLETATA**
Data: 2026-03-09
Obiettivo: Ridurre il debito tecnico, disaccoppiare la logica dalla UI, standardizzare il backend e migliorare la scalabilità del codice.

---

## 📊 Avanzamento Macro-Fasi
- [ ] **Fase 1: Standardizzazione Architettura Frontend (PySide6)**
- [ ] **Fase 2: Modularizzazione Logica di Business Desktop**
- [ ] **Fase 3: Refactoring e Pulizia Backend (FastAPI)**
- [ ] **Fase 4: Testing & Documentazione**

---

## 1️⃣ Fase 1: Standardizzazione Architettura Frontend (PySide6)
*Obiettivo: Separare l'interfaccia grafica (View), la gestione dello stato/logica di presentazione (ViewModel/Controller) e il puro aspetto visivo.*

### 1.1 Estrazione degli Stili (QSS)
- [ ] Creare una cartella `desktop_app/assets/styles/`.
- [ ] Rimuovere tutte le stringhe `self.setStyleSheet(...)` dalle classi View (es. `LoginView`, `DashboardView`).
- [ ] Spostare gli stili in file centralizzati come `main.qss`, `dark_theme.qss` e `light_theme.qss`.
- [ ] Modificare `desktop_app/main.py` per caricare globalmente i fogli di stile all'avvio.

### 1.2 Adozione del Pattern MVC/MVVM
Attualmente, le View (es. `ValidationView`) contengono logica per dialoghi di conferma, calcolo di date, manipolazione liste, e chiamate dirette all'`api_client`.
- [ ] **Model/State:** Definire modelli dati client-side (dataclasses/Pydantic) in `desktop_app/models/` per incapsulare i dati JSON ricevuti dall'API.
- [ ] **Controllers:** Creare controller specifici per ogni dominio in `desktop_app/controllers/` (es. `CertificatiController`, `DipendentiController`).
- [ ] **Views:** Le view devono essere "stupide". Rispondono solo ai segnali UI e notificano i controller.

### 1.3 Refactoring dei Componenti UI Riutilizzabili
- [ ] Estrarre le tabelle standard (es. con header interattivi e behavior di riga) in una classe custom in `desktop_app/widgets/data_table.py`.
- [ ] Estrarre la barra di ricerca/filtro in un widget indipendente `desktop_app/widgets/filter_bar.py`.
- [ ] Estrarre i widget di impaginazione e layout ripetitivi.

---

## 2️⃣ Fase 2: Modularizzazione Logica di Business Desktop
*Obiettivo: Rimuovere il "God Object" (ApplicationController/APIClient) e suddividere le responsabilità.*

### 2.1 Refactoring dell'`APIClient`
Attualmente `APIClient` (`desktop_app/api_client.py`) centralizza tutte le chiamate API, diventando un file enorme.
- [ ] Trasformare `APIClient` in un gestore di sessione HTTP base.
- [ ] Creare moduli repository/service client separati, ad es.:
  - `desktop_app/api/auth_api.py`
  - `desktop_app/api/certificati_api.py`
  - `desktop_app/api/dipendenti_api.py`
- [ ] Gestione standardizzata delle eccezioni HTTP (tramite decoratori o middleware).

### 2.2 Gestione Threading e Concorrenza (Qt)
Il codice attuale mescola `threading.Thread` nativo Python con i timer di Qt. Questo può portare a race conditions e blocchi della GUI.
- [ ] Sostituire le chiamate di rete in `threading.Thread` all'interno delle View con **`QThread`** e **`QRunnable`**.
- [ ] Creare un `WorkerManager` in `desktop_app/utils/worker.py` basato su `QThreadPool` per le richieste API asincrone, emettendo segnali Qt `(on_success, on_error)` per un aggiornamento thread-safe della UI.
- [ ] Risolvere/adattare i `TaskRunner` bloccanti usando pattern nativi asincroni.

---

## 3️⃣ Fase 3: Refactoring e Pulizia Backend (FastAPI)
*Obiettivo: Assicurare che il backend segua una vera "Clean Architecture".*

### 3.1 Separazione Livelli (Router vs Service)
I file in `app/api/routers/` non devono contenere logica di business o query complesse al database.
- [ ] Revisionare ogni endpoint in `app/api/routers/`.
- [ ] Spostare la logica CRUD nei file di servizio corrispondenti in `app/services/` (es. `app/services/dipendente_service.py`).
- [ ] Il router deve solo occuparsi di Dependency Injection (db session, utente corrente), validazione input (Pydantic schemas) e risposte HTTP.

### 3.2 Ottimizzazione Database e Pydantic
- [ ] Revisionare `app/db/models.py` per garantire l'uso corretto di indici su colonne molto interrogate (es. matricola, categoria).
- [ ] Separare i file degli schemi Pydantic (`app/schemas/`) per dominio (es. `schemas/dipendenti.py`, `schemas/certificati.py`) invece di usare moduli enormi.
- [ ] Passare uniformemente alla sintassi Pydantic V2 (`model_validate`, `model_dump` al posto di `from_orm`, `dict`).

### 3.3 Gestione Sicurezza e Configurazioni
- [ ] Consolidare le costanti cablate in `app/core/constants.py` e spostare quelle dinamiche in `app/core/config.py` (usando Pydantic BaseSettings).
- [ ] Rivedere la logica del `lock_manager.py` (database in sola lettura) per assicurarne la robustezza in caso di crash anomali dei client.

---

## 4️⃣ Fase 4: Testing & Documentazione
*Obiettivo: Garantire che i cambiamenti siano protetti e la documentazione aggiornata.*

### 4.1 Unit Testing Aggiornato
- [ ] **Backend**: Aumentare la copertura di `pytest` per i service layer isolati.
- [ ] **Frontend**: Implementare test base per i ViewModel/Controller estratti nella Fase 1, che essendo disaccoppiati dalla UI Qt (PySide6), possono essere testati senza `QApplication`.

### 4.2 Documentazione
- [ ] Aggiornare `docs/API_DOCUMENTATION.md` in base alla nuova struttura `APIClient`.
- [ ] Aggiornare `docs/DEVELOPER_ONBOARDING.md` menzionando PySide6, QSS e la struttura MVVM.
- [ ] Ripulire codice commentato obsoleto (riferimenti a vecchi import Tkinter).

---
## 🚀 Strategia di Esecuzione Proposta
1. Inizieremo estraendo gli **Stili (QSS)** per "pulire" immediatamente il codice visivo delle View.
2. Applicheremo la scomposizione dell'**APIClient** (Fase 2.1), che è la parte centrale per l'accesso ai dati.
3. Gradualmente trasformeremo le **View** (Fase 1.2 e 1.3), una ad una, implementando `QThreadPool`.
4. Sposteremo l'attenzione sul **Backend** (Fase 3) consolidando i servizi.
