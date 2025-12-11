# Sistema di Notifiche e Reportistica

Il modulo `app.services.notification_service.py` gestisce la generazione di report PDF e l'invio di email di alert per le scadenze.

## 1. Architettura

Il sistema opera in background gestito da `APScheduler` (configurato in `app.main.lifespan`).
È thread-safe grazie a un `threading.Lock` globale (`_email_lock`) che impedisce esecuzioni sovrapposte.

---

## 2. Generazione Report (In-Memory PDF)

Il report non viene mai scritto su disco (filesystem-free) per evitare problemi di permessi o race conditions. Viene generato interamente in RAM come stream di byte.

### Libreria: `fpdf2`
*   **Header**: Logo aziendale + Data odierna.
*   **Footer**: Numerazione pagine e disclaimer "Restricted".
*   **Tabelle**: Logica custom per gestire il page-break automatico all'interno delle tabelle.

### Struttura Report
Il PDF contiene tre sezioni dinamiche:
1.  **Certificati in Scadenza** (Soglia Standard).
2.  **Visite Mediche in Scadenza** (Soglia Visite).
3.  **Certificati Scaduti** (Non ancora rinnovati).

*Categorie Escluse*: 'ATEX', 'BLSD', 'DIRETTIVA SEVESO', 'DIRIGENTI E FORMATORI', 'H2S', 'MEDICO COMPETENTE', 'HLO'.

---

## 3. Invio Email (SMTP)

Il servizio supporta i protocolli SMTP più diffusi con negoziazione automatica della sicurezza.

### Configurazione (`settings.json`)
*   `SMTP_HOST`, `SMTP_PORT`, `SMTP_USER`, `SMTP_PASSWORD`
*   `EMAIL_RECIPIENTS_TO`, `EMAIL_RECIPIENTS_CC`

### Logica di Connessione
1.  **Porta 465**: Usa `smtplib.SMTP_SSL` (Connessione cifrata dall'inizio).
2.  **Porta 587/25**: Usa `smtplib.SMTP` + `starttls()` (Upgrade cifratura).

### Composizione Email
Messaggio MIME Multipart:
*   **Body HTML**: Riepilogo numerico delle scadenze e logo embedded (CID).
*   **Allegato**: Il PDF generato in memoria (`application/octet-stream`).

---

## 4. Trigger e Automazione

### Automatico (Scheduler)
Eseguito ogni giorno alle ore 08:00 (configurabile).

### Manuale (API)
Endpoint `POST /notifications/send-manual-alert` invocato dal pulsante "Genera Email" nella vista Scadenzario.

### Audit
Ogni invio (successo o fallimento) viene registrato nella tabella `audit_logs` con categoria `SYSTEM`.
