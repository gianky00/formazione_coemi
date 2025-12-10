# Istruzioni di Build, Distribuzione e Gestione Licenze

Questo documento tecnico descrive la procedura "Master" per compilare, proteggere e distribuire l'applicazione Intelleo.

## 1. Ambiente di Build (Requisiti)

*   **OS**: Windows 10/11 (Architettura x64).
*   **Python**: 3.12+ (Aggiunto al PATH).
*   **Node.js**: 18+ (Per buildare `guide_frontend`).
*   **Inno Setup**: v6.2+ (Installato in `C:\Program Files (x86)\Inno Setup 6`).
*   **PyArmor**: v8.5+ (Licenza Pro/Basic richiesta per offuscamento avanzato).
*   **Dipendenze**:
    ```bash
    pip install -r requirements.txt
    cd guide_frontend && npm install
    ```

## 2. Master Build Script (`admin/offusca/build_dist.py`)

L'intero processo è orchestrato dallo script `build_dist.py`. Non eseguire i passaggi manualmente a meno che non sia necessario per il debug.

### Esecuzione
Dalla root del progetto:
```bash
python admin/offusca/build_dist.py
```

### Pipeline di Build (Fasi)
1.  **Frontend Compilation**: Esegue `npm run build` in `guide_frontend`. Genera gli asset statici in `guide_frontend/dist/`.
2.  **Environment Check**: Verifica la presenza di compilatori C++ (MSVC) e Inno Setup.
3.  **Obfuscation (PyArmor)**:
    *   Protegge i package `app` e `desktop_app`.
    *   Genera runtime in `dist/obf/`.
    *   Applica regole: `restrict mode 2`, `mix-str`, `assert-call`.
4.  **Packaging (PyInstaller)**:
    *   Legge `Intelleo.spec` (o configurazione interna).
    *   Analizza import nascosti (Hidden Imports).
    *   Genera `dist/Intelleo/` (Directory).
5.  **DLL Injection**:
    *   Identifica le dipendenze di sistema critiche (`vcruntime140.dll`, `msvcp140.dll`).
    *   Le copia nella cartella `dll/` del pacchetto per garantire l'esecuzione su macchine "pulite".
6.  **Installer Creation (Inno Setup)**:
    *   Compila `admin/crea_setup/setup_script.iss`.
    *   Output finale: `dist/Intelleo_Setup_{version}.exe`.

---

## 3. Gestione e Generazione Licenze

Il sistema di licenze richiede la generazione di 3 file coordinati.

### Tool di Generazione
Eseguire:
```bash
python admin/crea_licenze/admin_license_gui.py
```

### Workflow Operativo
1.  **Input Dati**:
    *   **Hardware ID**: Seriale Disco del cliente (o MAC).
    *   **Scadenza**: Data (YYYY-MM-DD).
    *   **Nome Cliente**: Per organizzazione file.
2.  **Generazione**:
    *   Lo script chiama PyArmor CLI per generare `pyarmor.rkey` (Node-Locked).
    *   Lo script cifra i metadati in `config.dat` (Fernet).
    *   Lo script calcola SHA256 e crea `manifest.json`.
3.  **Output**:
    Viene creata una cartella `Licenza` contenente:
    *   `pyarmor.rkey` (Runtime Key)
    *   `config.dat` (UI Data)
    *   `manifest.json` (Integrity Check)

### Distribuzione (Auto-Update)
Per abilitare l'aggiornamento automatico della licenza:
1.  Accedere al **Repository GitHub Privato** delle licenze.
2.  Navigare in `licenses/`.
3.  Creare una cartella con il nome esatto dell'**Hardware ID** del cliente.
4.  Caricare i 3 file (`pyarmor.rkey`, `config.dat`, `manifest.json`) in quella cartella.
5.  Al prossimo avvio (o errore licenza), l'app scaricherà automaticamente i nuovi file.

---

## 4. Troubleshooting Build

### Errore "Module Not Found" in Runtime
*   **Causa**: PyInstaller non ha rilevato un import dinamico.
*   **Soluzione**: Aggiungi il modulo a `hiddenimports` in `build_dist.py`.

### Errore "DLL Load Failed"
*   **Causa**: Mancano le librerie ridistribuibili VC++ sul target.
*   **Soluzione**: Verificare che la fase "DLL Injection" abbia copiato le DLL corrette in `dist/Intelleo/dll/`.

### PyArmor "License Invalid" durante la Build
*   Assicurarsi che il file `pyarmor-regcode-xxxx.txt` sia stato registrato sulla macchina di build (`pyarmor reg pyarmor-regcode...`).
