# Workflow di Distribuzione e Licenze

Questo documento guida il processo operativo per distribuire il software ai clienti e gestire il ciclo di vita delle licenze.

## 1. Prima Distribuzione (New Customer)

### Passo 1: Build dell'Eseguibile
Se non hai già una build recente:
1.  Esegui `python admin/offusca/build_nuitka.py --clean`.
2.  Compila installer: `"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" admin/crea_setup/setup_script.iss`
3.  Preleva l'installer da `dist/installer/Intelleo_Setup_vX.X.exe`.

### Passo 2: Installazione
Invia l'installer al cliente.
*   Il cliente installa il software.
*   Al primo avvio, l'app mostrerà un errore di licenza e fornirà l'**Hardware ID** (Disk Serial).

### Passo 3: Generazione Licenza
1.  Ricevi l'Hardware ID dal cliente.
2.  Esegui `python admin/crea_licenze/admin_license_gui.py`.
3.  Inserisci Hardware ID e Scadenza.
4.  Genera. Otterrai una cartella `Licenza` con 3 file (`pyarmor.rkey`, `config.dat`, `manifest.json`).

### Passo 4: Attivazione
*   **Metodo Manuale**: Invia la cartella `Licenza` (zippata) al cliente. Lui deve estrarla nella cartella di installazione o in `%LOCALAPPDATA%/Intelleo/Licenza`.
*   **Metodo Auto-Update** (Consigliato per rinnovi): Vedi sezione 2.

---

## 2. Rinnovo Licenza (Auto-Update)

Per rinnovare una licenza scaduta senza disturbare il cliente con file zip:

1.  Genera la nuova licenza (Passo 3 sopra) con la nuova data di scadenza.
2.  Accedi al **Repo GitHub Privato** ("License CDN").
3.  Vai in `licenses/{HARDWARE_ID_CLIENTE}/`.
    *   *Se non esiste, crea la cartella.*
4.  Carica/Sovrascrivi i 3 file generati.
5.  **Fatto**.
    *   Al prossimo avvio, l'app del cliente rileverà che la licenza locale è scaduta.
    *   Contatterà GitHub, vedrà il nuovo `manifest.json`.
    *   Scaricherà e applicherà i file trasparentemente.

---

## 3. Gestione Emergenze

### Licenza "Tampered" o Corrotta
Se il cliente vede un errore di integrità:
1.  Chiedi di cancellare la cartella `%LOCALAPPDATA%/Intelleo/Licenza`.
2.  L'app tenterà di riscaricare tutto da GitHub al riavvio.

### Cambio PC
Se il cliente cambia PC, l'Hardware ID cambierà.
1.  Ottenere il nuovo Hardware ID.
2.  Generare nuova licenza.
3.  Creare nuova cartella su GitHub.
4.  Il cliente dovrà ricevere la prima licenza manualmente (o via GitHub se l'app riesce a connettersi in recovery mode).
