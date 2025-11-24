# Istruzioni per la Build e la Gestione Licenze

Questo documento spiega come creare la distribuzione dell'applicazione Intelleo protetta con PyArmor e come gestire le licenze.

## Prerequisiti

1.  **Python 3.12+** installato e aggiunto al PATH.
2.  **Inno Setup 6** installato (standard path: `C:\Program Files (x86)\Inno Setup 6`).
3.  **Virtual Environment** attivato con le dipendenze installate:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Licenza PyArmor**: È necessario disporre di una licenza **PyArmor 8/9 Basic** (o superiore) attiva e registrata sulla macchina di build.

## 1. Creare la Distribuzione (Master Build)

È stato creato uno script automatizzato che gestisce l'intero ciclo di rilascio: build del frontend React, offuscamento Python, packaging PyInstaller e creazione installer Inno Setup.

Esegui il comando dalla root del progetto:

```bash
python admin/offusca/build_dist.py
```

**Fasi dello Script:**
1.  **React Build**: Compila `guide_frontend` in `guide_frontend/dist/`.
2.  **Offuscamento**: Esegue `pyarmor gen` su `app` e `desktop_app`.
3.  **Packaging**: Esegue `PyInstaller` per creare la cartella di distribuzione.
4.  **DLL Injection**: Copia le DLL di sistema (es. `vcruntime140.dll`) nella cartella `dll/` della distribuzione per massimizzare la portabilità.
5.  **Installer**: Compila il setup finale (`MyshopSetup.exe` o simile) usando `ISCC.exe`.

**Output:**
*   **Cartella Portable**: `dist/Intelleo/`
*   **Installer**: `dist/Intelleo_Setup.exe` (o nome definito nello script Inno).

## 2. Gestione delle Licenze

### Generazione Licenze (Lato Amministratore)
Per generare nuove licenze per i clienti, utilizza l'interfaccia grafica dedicata situata nella root:

```bash
python admin_license_gui.py
```

1.  **Hardware ID**: (Opzionale) Incolla l'ID hardware del cliente per vincolare la licenza.
2.  **Scadenza**: Imposta la data di scadenza.
3.  Clicca su **Genera Licenza**.

Il file `pyarmor.rkey` e il file cifrato `config.dat` verranno salvati in una sottocartella `Licenza/` all'interno della cartella cliente. Invia l'intera cartella `Licenza` al cliente.

### Installazione Licenza (Lato Cliente)
Il cliente deve copiare la cartella `Licenza` (contenente `pyarmor.rkey` e `config.dat`) all'interno della directory di installazione (es. `C:\Users\Nome\AppData\Local\Programs\Intelleo`).

*Nota: L'installer crea automaticamente questa struttura.*

### Recupero Hardware ID (Lato Cliente)
1.  Lanciare l'applicazione. Se la licenza è scaduta o mancante, un messaggio mostrerà l'Hardware ID.
2.  Da riga di comando:
    ```bash
    Intelleo.exe --hwid
    ```
