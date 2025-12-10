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

## 2. Master Build Script (`admin/offusca/build_nuitka.py`)

L'intero processo è orchestrato dallo script `build_nuitka.py`. Sostituisce completamente il vecchio script PyInstaller (`build_dist.py`).

### Esecuzione
Dalla root del progetto:
```bash
python admin/offusca/build_nuitka.py [--clean] [--fast] [--skip-checks]
```

**Opzioni**:
- `--clean`: Rimuove build precedenti prima di compilare
- `--fast`: Build veloce senza LTO (per sviluppo/test)
- `--skip-checks`: Salta verifica ambiente (non raccomandato)

### Pipeline di Build (Fasi)
1.  **Verifica Ambiente**: Check Python 3.12+, Nuitka, MSVC compiler, npm.
2.  **Build React Frontend**: Compila `guide_frontend/` se necessario (`npm run build`).
3.  **Compilazione Nuitka**:
    *   **Analisi Python** (~5-10 min prima volta): Analizza import e dipendenze.
    *   **Generazione Codice C** (~2-5 min): Converte Python in C.
    *   **Compilazione C** (~20-30 min prima volta, ~8 min con ccache): Compila con MSVC.
    *   **Linking** (~2-5 min): Crea eseguibile finale.
4.  **Post-Processing**: Crea README.txt, verifica output, copia asset extra.
5.  **Report**: Genera statistiche build (tempo, dimensione, file count).

**⏱️ Tempi Totali**:
- Prima compilazione: **35-50 minuti**
- Successive (con ccache): **8-15 minuti**

💡 **Tip**: Installa `ccache` per velocizzare rebuild: `choco install ccache`

### Output
```
dist/nuitka/
└── Intelleo.dist/
    ├── Intelleo.exe          # Eseguibile principale (nativo C)
    ├── guide/                # React SPA
    │   └── index.html
    ├── desktop_app/
    │   ├── assets/
    │   └── icons/
    ├── Qt6Core.dll           # Dipendenze Qt
    ├── python312.dll         # Runtime Python
    └── [altre DLL]
```

### Installer Creation
Dopo il build Nuitka, crea l'installer:
```bash
cd admin/crea_setup
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_script.iss
```
Output: `dist/installer/Intelleo_Setup_v2.0.0.exe`

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

### Errore "Module 'X' not found" in Runtime
*   **Causa**: Nuitka non ha rilevato un import dinamico.
*   **Soluzione**: Aggiungi al comando Nuitka in `build_nuitka.py`:
    ```python
    "--include-module=X",
    ```

### Errore "DLL Load Failed"
*   **Causa**: Mancano le librerie ridistribuibili VC++ sul target.
*   **Soluzione**: L'utente deve installare Visual C++ Redistributable da Microsoft, oppure includere `vc_redist.x64.exe` nell'installer.

### Build si blocca su "Compiling X.c" per >10 minuti
*   **Causa**: File C grande o RAM insufficiente.
*   **Soluzione**:
    - Verifica RAM disponibile (>8 GB raccomandati)
    - Chiudi altri programmi
    - Aspetta (alcuni file richiedono 5-10 min)
    - Se persiste, usa `--fast` per disabilitare LTO

### ccache non attivo (ogni build compila tutto)
*   **Causa**: ccache non installato o non nel PATH.
*   **Soluzione**:
    ```bash
    # Windows (Chocolatey)
    choco install ccache
    
    # Verifica
    ccache --version
    ccache -s  # Mostra statistiche cache
    ```

### Errore "MSVC not found"
*   **Causa**: Visual Studio Build Tools non installato.
*   **Soluzione**: Installa "Build Tools for Visual Studio 2022" con workload "Desktop development with C++".

### Prima compilazione molto lenta (>50 min)
*   **Causa**: Normale per ~1200 moduli C da compilare.
*   **Soluzione**: 
    - Usa `--fast` per test rapidi
    - Installa `ccache` per build successive più veloci
    - Non interrompere il processo
