# Guida al Workflow di Licenza e Distribuzione

## Risposta alla tua domanda: "Prima offuscare o prima la licenza?"

**Devi PRIMA offuscare (compilare) il codice.**

### Perché?
La licenza che generi (`pyarmor.rkey`) deve essere compatibile con il "Runtime" (il motore di sicurezza) che viene creato durante la fase di offuscamento.

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
Invia `Intelleo.exe` e il file `get_client_info.bat` al cliente.
**Nota:** Senza licenza, l'app non funzionerà ancora.

### 3. Ottenere l'ID Hardware del Cliente
Il metodo standard è usare lo script batch, che recupera il **Seriale del Disco** e il **MAC Address**.

1.  Chiedi al cliente di eseguire `get_client_info.bat`.
2.  Il cliente ti invierà il testo copiato (es. Seriale Disco: `50026B78...`).

### 4. Generare la Licenza
Una volta che hai il seriale (es. `50026B7882000000`), sul tuo PC esegui:
```bash
python admin_license_gui.py
```
*   Incolla il seriale nel campo "Hardware ID".
    *   *Nota:* Se vuoi legarlo anche al MAC address, puoi incollare entrambi o una combinazione, ma di solito il Seriale Disco è sufficiente e più stabile.
*   Imposta la scadenza.
*   Clicca "Genera Licenza".

### 5. Attivazione
Invia il file generato `dist/pyarmor.rkey` al cliente.
Il cliente deve metterlo nella stessa cartella di `Intelleo.exe`.
Al prossimo avvio, l'app funzionerà.
