# Report Tecnico di Design del Sistema (System Design Document)

**Versione Documento**: 1.0.0
**Ambito**: Architettura di Sicurezza, Gestione Licenze e Pipeline di Aggiornamento
**Classificazione**: CONFIDENTIAL / INTERNAL TECHNICAL

---

## 1. Introduzione ed Obiettivi

Il presente documento espone l'architettura tecnica dettagliata dei sottosistemi critici di **Intelleo**, ricostruita attraverso l'analisi ingegneristica del codice sorgente (Reverse Engineering). Il report si focalizza sui meccanismi di protezione della proprietà intellettuale (IP), integrità del sistema e distribuzione sicura degli aggiornamenti di licenza.

L'architettura segue un approccio **"Zero-Trust Local"**, assumendo che l'ambiente di esecuzione (il PC del cliente) sia potenzialmente ostile o compromesso (es. data di sistema alterata, file spostati).

---

## 2. Gestione e Ingegneria delle Licenze

Il sistema di licenze adotta un approccio ibrido che combina **Node-Locking Hardware** (tramite PyArmor) e **Configurazione Crittografata** (tramite AES-128/Fernet) per garantire che l'applicazione giri solo sull'hardware autorizzato e nel periodo di validità contrattuale.

### 2.1 Flussi Crittografici e Primitive

Il sistema utilizza primitive crittografiche standard per garantire confidenzialità e integrità.

*   **Algoritmo Simmetrico**: Fernet (implementazione basata su AES-128 in modalità CBC con padding PKCS7 e autenticazione HMAC-SHA256).
*   **Gestione Chiavi (Key Management)**:
    *   La *Master Key* è hardcoded nel binario ma protetta tramite offuscamento XOR in memoria (`app.core.license_security`).
    *   **Secret**: `b'8kHs_rmwqaRUk1AQLGX65g4AEkWUDapWVsMFUQpN9Ek='` (Valore statico condiviso).
    *   **Salt**: Non applicabile (Shared Secret statico per portabilità offline).
*   **Formato Licenza (`config.dat`)**:
    *   Payload JSON serializzato, cifrato con Fernet.
    *   Contenuto: `Hardware ID`, `Scadenza Licenza` (DD/MM/YYYY), `Cliente`, `Generato il`.

### 2.2 Node-Locking e Fingerprinting Hardware

Il vincolo all'hardware (Node-Locking) è implementato nel modulo `desktop_app.services.hardware_id_service`.

**Algoritmo di Fingerprinting:**
1.  **Primary Binding (Windows)**: Interrogazione WMI (`Win32_DiskDrive`).
    *   Target: `PHYSICALDRIVE0` (Disco di avvio primario).
    *   Valore estratto: `SerialNumber` (con rimozione di punti o spazi finali).
    *   *Nota Tecnica*: L'uso di `pythoncom.CoInitialize`/`CoUninitialize` garantisce la stabilità dei thread durante le chiamate COM.
2.  **Fallback Binding**: Indirizzo MAC (`uuid.getnode()`).
    *   Formattazione: Hex string (es. `00:1A:2B:3C:4D:5E`).

**Pseudocodice di Rilevamento:**
```python
FUNCTION GetHardwareID():
    IF OS is Windows:
        TRY:
            Initialize COM
            DiskSerial = WMI.Query("SELECT SerialNumber FROM Win32_DiskDrive WHERE DeviceID='PHYSICALDRIVE0'")
            IF DiskSerial IS VALID:
                RETURN Normalize(DiskSerial)
        CATCH Error:
            LogWarning("WMI Failed")
        FINALLY:
            Uninitialize COM

    # Fallback Universale
    MacAddr = GetMacAddress()
    RETURN FormatHex(MacAddr)
```

### 2.3 Macchina a Stati del Ciclo di Vita (License Lifecycle)

Il ciclo di vita è governato da una macchina a stati implementata in `launcher.py` (Gatekeeper) e `desktop_app.services.license_manager.py`.

| Stato | Condizione | Comportamento Sistema |
| :--- | :--- | :--- |
| **VALID** | File presenti, firma valida, `Today <= Scadenza`, Hardware ID match. | Avvio normale dell'applicazione. |
| **EXPIRING_SOON** | `Valid` AND `Today > Scadenza - 7 giorni`. | Avvio normale + Warning UI ("Rinnovare entro X giorni"). |
| **EXPIRED** | `Today > Scadenza`. | **Blocco Avvio**. Trigger procedura di Auto-Update. |
| **TAMPERED** | Data sistema incoerente o File corrotti (Checksum fail). | **Blocco Avvio**. Trigger procedura di Auto-Update. |
| **MISSING** | File `pyarmor.rkey` o `config.dat` assenti. | **Blocco Avvio**. Trigger procedura di Auto-Update. |

### 2.4 Anti-Tamper Temporale (Time Service)

Per prevenire l'alterazione dell'orologio di sistema (es. impostare la data nel passato per estendere la licenza), il modulo `desktop_app.services.time_service` implementa un controllo avanzato.

**Logica di Validazione Temporale:**
1.  **Check NTP (Prioritario)**: Tenta connessione a `pool.ntp.org`.
    *   Se discrepanza `|NetworkTime - SystemTime| > 5 minuti` -> **BLOCCO (Tampering Rilevato)**.
    *   Se OK -> Aggiorna `secure_time.dat` (Cifrato) con `LastOnlineCheck` e `LastExecution`.
2.  **Check Offline (Fallback)**: Carica `secure_time.dat`.
    *   **Anti-Rollback**: Se `SystemTime < LastExecution` -> **BLOCCO**.
    *   **Offline Buffer**: Se `SystemTime > LastOnlineCheck + 3 Giorni` -> **BLOCCO (Forza Connessione)**.

---

## 3. Pipeline di Aggiornamento Automatico (License Auto-Update)

Il sistema implementa una pipeline di aggiornamento "Pull-based" specifica per i file di licenza, utilizzando GitHub come Content Delivery Network (CDN) sicuro. Non è presente un sistema di aggiornamento automatico per l'eseguibile software (.exe).

### 3.1 Architettura e Protocollo

*   **Endpoint**: Repository GitHub Privato.
*   **Path**: `/licenses/{HardwareID}/`.
*   **Autenticazione**: Personal Access Token (PAT) recuperato dinamicamente via API `/config/updater`.

### 3.2 Flusso di Aggiornamento (Logic Flow)

1.  **Detection**: Il `Launcher` rileva uno stato di errore (Licenza scaduta/mancante).
2.  **Config Fetch**: Recupera le credenziali di aggiornamento (Repo/Token) dal backend (o hardcoded in recovery mode).
3.  **Manifest Retrieval**: Scarica `manifest.json` remoto.
    *   Contiene: SHA256 dei file `pyarmor.rkey` e `config.dat`.
4.  **Differential Check**:
    *   Calcola SHA256 dei file locali (se esistenti).
    *   Se `LocalHash == RemoteHash` -> Nessuna azione (Up-to-date).
5.  **Download & Verify**:
    *   Scarica i file in una directory temporanea (`tempfile`).
    *   Verifica immediata: `SHA256(DownloadedFile) == ManifestHash`.
    *   Se mismatch -> **Abort** (Previene corruzione o Man-in-the-Middle).
6.  **Atomic Replacement**:
    *   Utilizza `shutil.move` per sovrascrivere i file nella directory `Licenza` dell'utente.
    *   Questa operazione è atomica su filesystem POSIX, quasi-atomica su Windows.

**Pseudocodice di Aggiornamento:**
```python
FUNCTION UpdateLicense(HardwareID):
    Manifest = HTTP_GET(GitHub + "/manifest.json")

    FOR File IN ["pyarmor.rkey", "config.dat"]:
        RemoteHash = Manifest[File]
        LocalHash = CalculateSHA256(LocalPath + File)

        IF LocalHash != RemoteHash:
            TempFile = Download(GitHub + "/" + File)
            IF CalculateSHA256(TempFile) != RemoteHash:
                RAISE SecurityError("Checksum Mismatch")

            Move(TempFile, LocalPath + File) # Atomic Replace

    RETURN Success("Restart Required")
```

---

## 4. Discovery e Rilevamento Ambiente

Il sistema implementa logiche robuste per determinare l'ambiente di esecuzione e localizzare le risorse critiche (Database, Licenze), garantendo portabilità e resilienza.

### 4.1 License Discovery (Crawling)

All'avvio, il sistema scansiona posizioni multiple per trovare una licenza valida. Questo permette la migrazione trasparente tra versioni o installazioni.

**Path Priority Queue:**
1.  **User Data (RW)**: `%LOCALAPPDATA%/Intelleo/Licenza/` (Standard corrente).
2.  **Legacy Install (RO)**: `{InstallDir}/Licenza/` (Retro-compatibilità).
3.  **Root Install (RO)**: `{InstallDir}/` (Fallback estremo).

### 4.2 Database Discovery & Recovery

Il database `database_documenti.db` viene cercato secondo la configurazione in `settings.json`.
In caso di fallimento (File mancante o Header corrotto), il sistema entra in **Recovery Mode**:
1.  Il Backend non crasha ma segnala errore allo stato di salute.
2.  Il Frontend visualizza un **Recovery Dialog** (gestito in `launcher.py`).
3.  Opzioni utente:
    *   *Sfoglia*: Ricollega un DB esistente o Backup (`.bak`).
    *   *Crea*: Inizializza un nuovo DB vuoto con schema e seed utente Admin.

### 4.3 Environment Detection

*   **Frozen Detection**: Usa `getattr(sys, 'frozen', False)` per distinguere tra Dev (Python script) e Prod (eseguibile compilato).
*   **Path Resolution** (via `app.core.path_resolver`):
    *   `get_base_path()`: Determina root app in modo universale
    *   Se Frozen + Nuitka: Usa `os.path.dirname(sys.executable)`
    *   Se Frozen + PyInstaller (legacy): Usa `sys._MEIPASS`
    *   Se Dev: Usa `Path(__file__).resolve().parent.parent.parent`
*   **DLL Injection**: Inietta dinamicamente la cartella `dll/` nel `PATH` e via `os.add_dll_directory` per garantire il caricamento delle dipendenze C++ (Qt, MSVC) su Windows.

### 4.4 String Obfuscation (Security)

Con la migrazione a Nuitka (codice C nativo), le stringhe sensibili vengono offuscate per evitare estrazione con `strings`:

*   **Modulo**: `app/core/string_obfuscation.py`
*   **Algoritmo**: XOR con chiave statica + Base64 encoding
*   **Applicato a**: Chiavi Fernet, API keys, token
*   **Validazione**: `strings Intelleo.exe | grep "8kHs"` deve essere vuoto
