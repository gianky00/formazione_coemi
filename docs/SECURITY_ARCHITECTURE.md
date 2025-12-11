# Architettura di Sicurezza e Licensing

Questo documento descrive i meccanismi di protezione implementati in Intelleo per garantire la sicurezza dei dati, la protezione della proprietà intellettuale (IP) e l'integrità del sistema.

## 1. Modello di Sicurezza "Zero-Trust Local"

L'architettura assume che l'ambiente di esecuzione (il PC del cliente) sia potenzialmente non sicuro.

### Database Cifrato (Data-at-Rest)
*   **Algoritmo**: AES-128 (via Fernet).
*   **Implementazione**: `app.core.db_security.DBSecurityManager`.
*   **Funzionamento**:
    *   Il file su disco è *sempre* cifrato.
    *   All'avvio, viene letto, decifrato in RAM e caricato in `sqlite3` (`:memory:`).
    *   Al salvataggio, il dump della memoria viene cifrato e sovrascritto atomicamente.
*   **Crash Safety**: Lock file (`.lock`) su descrittore file per evitare scritture concorrenti.

### Protezione Segreti
*   **Obfuscation**: Le stringhe sensibili (API Keys, Token) nel codice sorgente sono protette tramite XOR + Base64 (`app.core.string_obfuscation.py`) per resistere all'analisi statica (`strings`).
*   **Runtime**: I segreti sono decifrati solo al momento dell'uso.

---

## 2. Sistema di Licenze (Node-Locking)

Il sistema vincola l'esecuzione del software all'hardware specifico del cliente.

### 2.1 Hardware Fingerprinting
Implementato in `desktop_app.services.hardware_id_service`.
1.  **Primary (Windows)**: Serial Number del disco di avvio (`PHYSICALDRIVE0`) via WMI.
2.  **Fallback**: Indirizzo MAC della scheda di rete.

### 2.2 File di Licenza
Richiede la presenza contemporanea di due file in `%LOCALAPPDATA%/Intelleo/Licenza/`:
1.  **`pyarmor.rkey`**: Chiave crittografica generata da PyArmor (Protezione Runtime codice Python).
2.  **`config.dat`**: Payload JSON cifrato (AES-128) contenente i metadati (Scadenza, Nome Cliente, Hardware ID).

### 2.3 Anti-Tamper Temporale
Per prevenire l'alterazione dell'orologio di sistema (Backdating):
*   **NTP Check**: Verifica l'ora con `pool.ntp.org` all'avvio.
*   **Consistency Check**: Se l'ora di sistema è precedente all'ultima esecuzione registrata (`secure_time.dat`), l'avvio viene bloccato.

---

## 3. Pipeline di Aggiornamento Licenze

Il sistema supporta l'aggiornamento automatico delle licenze senza reinstallazione software.

### Workflow "Pull-Based"
1.  **Trigger**: Avvio fallito per licenza scaduta o non valida.
2.  **Auth**: Il client si autentica su un Repository GitHub Privato usando un Token limitato.
3.  **Fetch**: Cerca nella cartella `/licenses/{HARDWARE_ID}/`.
4.  **Verifica**: Scarica il `manifest.json` contenente gli hash SHA256 dei file.
5.  **Download Sicuro**: Scarica `pyarmor.rkey` e `config.dat` verificando l'hash.
6.  **Atomic Swap**: Sostituisce i file locali solo se la verifica passa.

---

## 4. Audit Logging

Tutte le azioni sensibili sono registrate nella tabella `audit_logs` del database.

*   **Categorie**: `AUTH`, `CERTIFICATE`, `SYSTEM`, `SECURITY`.
*   **Dati**:
    *   `severity`: LOW, MEDIUM, CRITICAL.
    *   `ip_address`, `device_id`.
    *   `changes`: JSON diff dello stato prima/dopo (snapshot).
*   **Trigger Alert**: Eventi CRITICAL (es. Brute Force, Admin Login abusivo) scatenano invio email immediato.
