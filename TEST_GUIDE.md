# Guida al Test della Distribuzione

La build è stata completata con successo. Ecco i passaggi per verificare che tutto funzioni correttamente.

## 1. Verifica Eseguibile
Vai nella cartella:
`dist/package/`

Troverai il file `Intelleo.exe`.

## 2. Test ID Hardware (Simulazione Cliente)
1.  Apri un terminale (Prompt dei Comandi o PowerShell) in quella cartella.
2.  Esegui:
    ```bash
    Intelleo.exe --hwid
    ```
    **Risultato atteso**: Deve stampare una stringa alfanumerica (l'ID della macchina) e uscire. NON deve stampare "N/A" o errori.

## 3. Generazione Licenza (Amministratore)
1.  Torna alla root del progetto ed esegui:
    ```bash
    python admin_license_gui.py
    ```
2.  Clicca su **"Rileva ID Locale"**.
    **Risultato atteso**: Deve riempire il campo con l'ID hardware corretto (lo stesso del punto 2).
3.  Imposta una data di scadenza e clicca **"Genera Licenza"**.
    **Risultato atteso**: Messaggio di successo "Licenza generata...".

## 4. Test Applicazione Completa
1.  Copia il file `pyarmor.rkey` generato (in `dist/`) nella cartella `dist/package/` accanto a `Intelleo.exe`.
2.  Esegui `Intelleo.exe` (doppio click).
    **Risultato atteso**: L'applicazione deve avviarsi, mostrare lo splash screen e caricare l'interfaccia principale senza errori di backend.

Se incontri ancora errori, invia il file `dist/package/debug_hwid.log`.
