# Guida al Workflow di Licenza e Distribuzione

## Risposta alla tua domanda: "Prima offuscare o prima la licenza?"

**Devi PRIMA offuscare (compilare) il codice.**

### Perché?
La licenza che generi (`pyarmor.rkey`) deve essere compatibile con il "Runtime" (il motore di sicurezza) che viene creato durante la fase di offuscamento. Ogni volta che esegui una build pulita, potrebbe essere generato un nuovo runtime, quindi la licenza deve corrispondere.

---

## Workflow Consigliato

Ecco la sequenza corretta per distribuire il software protetto:

### 1. Build (Offuscamento e Packaging)
Esegui sul tuo PC di sviluppo:
```bash
python build_dist.py
```
Questo crea l'eseguibile protetto in `dist/package/Intelleo.exe`.

### 2. Distribuzione Iniziale
Invia `Intelleo.exe` (e la cartella omonima se non è one-file, ma qui è one-file) al cliente.
**Nota:** Senza licenza, l'app non funzionerà ancora.

### 3. Ottenere l'ID Hardware del Cliente
Hai due metodi. **Il Metodo A è il più sicuro** perché garantisce che l'ID sia quello *esatto* che PyArmor si aspetta.

*   **Metodo A (Consigliato):**
    Chiedi al cliente di lanciare `Intelleo.exe`. Visto che manca la licenza, apparirà un messaggio di errore che mostra il suo **ID Hardware** (una stringa alfanumerica). Fattelo inviare.

*   **Metodo B (Script BAT):**
    Invia al cliente il file `get_client_info.bat`. Lui lo esegue e ti incolla il Seriale Disco / MAC Address.
    *Attenzione:* Se usi questo metodo, devi essere sicuro che PyArmor sia configurato per accettare esattamente quel formato di seriale come ID. Se PyArmor calcola l'ID in modo diverso (es. hash combinato), la licenza generata con il seriale grezzo potrebbe non funzionare.

### 4. Generare la Licenza
Una volta che hai l'ID (diciamo `XXXX-YYYY-ZZZZ` o il seriale disco), sul tuo PC esegui:
```bash
python admin_license_gui.py
```
*   Incolla l'ID nel campo "Hardware ID".
*   Imposta la scadenza.
*   Clicca "Genera Licenza".

### 5. Attivazione
Invia il file generato `dist/pyarmor.rkey` al cliente.
Il cliente deve metterlo nella stessa cartella di `Intelleo.exe`.
Al prossimo avvio, l'app funzionerà.
