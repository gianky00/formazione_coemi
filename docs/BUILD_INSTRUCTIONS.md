# Istruzioni per la Build e la Gestione Licenze

Questo documento spiega come creare la distribuzione dell'applicazione Intelleo protetta con PyArmor e come gestire le licenze.

## Prerequisiti

Assicurati di avere Python installato e le seguenti librerie:

```bash
pip install -r requirements.txt
pip install pyarmor pyinstaller
```

> **Nota Importante**: È necessario disporre di una licenza **PyArmor 9 Basic** (o superiore) attiva per utilizzare le funzionalità di offuscamento complete. Assicurati di aver registrato la tua licenza PyArmor sulla macchina di build.

## 1. Creare la Distribuzione (Eseguibile)

È stato creato uno script automatizzato per semplificare il processo di build. Questo script gestisce l'offuscamento del codice, la preparazione degli asset e il packaging finale.

Per creare l'eseguibile, esegui semplicemente:

```bash
python build_dist.py
```

**Cosa fa lo script:**
1.  **Offuscamento**: Esegue `pyarmor gen` per proteggere il codice sorgente (cartelle `app` e `desktop_app`).
2.  **Preparazione**: Copia il launcher e ripristina i punti di ingresso necessari per la gestione degli errori di licenza.
3.  **Packaging**: Esegue `PyInstaller` per creare un singolo file eseguibile (`.exe`).

**Output:**
L'eseguibile finale si troverà in:
`dist/package/Intelleo.exe`

## 2. Gestione delle Licenze

### Generazione Licenze (Lato Amministratore)
Per generare nuove licenze per i clienti, utilizza l'interfaccia grafica dedicata:

```bash
python admin_license_gui.py
```

1.  **Hardware ID**: (Opzionale) Incolla l'ID hardware del cliente per vincolare la licenza alla sua macchina specifica.
2.  **Scadenza**: Imposta la data di scadenza della licenza.
3.  Clicca su **Genera Licenza**.

Il file di licenza (`pyarmor.rkey`) verrà generato nella cartella `dist/`. Invia questo file al cliente.

### Installazione Licenza (Lato Cliente)
Il cliente deve posizionare il file `pyarmor.rkey` nella stessa cartella dell'eseguibile `Intelleo.exe`.
Al lancio, l'applicazione verificherà automaticamente la presenza e la validità della licenza.

### Recupero Hardware ID (Lato Cliente)
Se il cliente deve fornirti il suo Hardware ID:
1.  Può lanciare l'applicazione. Se la licenza manca o è scaduta, apparirà un messaggio di errore che mostra il suo **ID Hardware**.
2.  Se l'applicazione è attiva, può andare nel menu **Supporto -> ID Hardware** per visualizzare e copiare l'ID.
3.  In alternativa, può lanciare l'eseguibile da riga di comando con il flag `--hwid`:
    ```bash
    Intelleo.exe --hwid
    ```

## Struttura della Build
Il sistema di build utilizza un approccio ibrido per garantire sicurezza e usabilità:
*   **Codice Core**: I pacchetti `app` e `desktop_app` sono completamente offuscati.
*   **Launcher**: Un file `launcher.py` (incluso nell'exe) avvia il server backend e l'interfaccia grafica.
*   **Gestione Errori**: Il punto di ingresso principale intercetta gli errori di licenza PyArmor e mostra una GUI user-friendly invece di crashare, permettendo al cliente di vedere il proprio HWID.
