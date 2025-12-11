# Logica di Business Certificati

Questo documento dettaglia le regole di business implementate in `app.services.certificate_logic.py` per la gestione del ciclo di vita dei certificati e il calcolo degli stati.

## 1. Calcolo Scadenze

La data di scadenza (`data_scadenza_calcolata`) è determinata in due modi, con priorità gerarchica:

1.  **Esplicita (AI)**: Se l'AI estrae una data di scadenza dal documento (es. "Da rivedere entro il..."), questa viene utilizzata direttamente.
2.  **Calcolata (Validità)**: Se l'AI restituisce `null`, il sistema calcola la scadenza aggiungendo la `validita_mesi` della categoria alla `data_rilascio`.
    *   Formula: `data_rilascio + relativedelta(months=validita_mesi)`
    *   Eccezione: Categorie con `validita_mesi = 0` (es. "NOMINA", "HLO") non scadono mai, a meno che non sia presente una data esplicita.

---

## 2. Stati del Certificato

Lo stato è un valore dinamico calcolato a runtime (non persistito su DB per evitare disallineamenti).

| Stato | Condizione | Colore UI |
| :--- | :--- | :--- |
| **ATTIVO** | `data_scadenza` > oggi + soglia | Verde |
| **IN SCADENZA** | oggi <= `data_scadenza` <= oggi + soglia | Giallo |
| **SCADUTO** | `data_scadenza` < oggi | Rosso |
| **ARCHIVIATO** | Certificato scaduto E esiste un certificato più recente (data rilascio >) per lo stesso dipendente e stessa categoria. | Grigio |

### Soglie di Alert (`settings.json`)
*   **Standard**: `ALERT_THRESHOLD_DAYS` (Default: 60 gg) - Per corsi tecnici.
*   **Visite Mediche**: `ALERT_THRESHOLD_DAYS_VISITE` (Default: 30 gg) - Per "VISITA MEDICA".

---

## 3. Logica di Matching Dipendenti (`matcher.py`)

Quando viene caricato un certificato, il sistema tenta di associarlo automaticamente a un dipendente esistente.

### Algoritmo di Risoluzione
1.  **Matching per Nome**: Cerca corrispondenze esatte ("COGNOME NOME") o inverse ("NOME COGNOME").
2.  **Risoluzione Omonimie**:
    *   Se trova >1 dipendente con lo stesso nome, richiede la `data_nascita`.
    *   Se la `data_nascita` del certificato coincide con quella di un dipendente, associa.
    *   Altrimenti, fallisce l'associazione.
3.  **Handling Nomi Composti**: Supporta cognomi multipli (es. "De Luca") testando tutte le permutazioni di split.

### Certificati Orfani
Se l'associazione fallisce (es. Dipendente non trovato o Omonimia irrisolta):
*   `dipendente_id` rimane `NULL`.
*   I dati grezzi (`nome_dipendente_raw`, `data_nascita_raw`) vengono salvati nel record.
*   Stato Validazione: `DA_VALIDARE`.
*   Motivo Fallimento salvato in: `assegnazione_fallita_ragione`.
