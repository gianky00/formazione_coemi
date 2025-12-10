# Contribuire a Intelleo

Grazie per l'interesse nel contribuire a Intelleo! Poiché questo è un software proprietario e critico per la sicurezza, seguiamo protocolli rigidi.

## 1. Come Iniziare

1.  Leggi **[Dev Protocols](DEV_PROTOCOLS.md)**. È la bibbia dello stile di codice e della sicurezza.
2.  Leggi **[System Architecture](SYSTEM_ARCHITECTURE.md)** per capire dove mettere le mani.
3.  Assicurati che i test passino (`pytest`) prima di committare.

## 2. Segnalazione Bug

Usa il tracker delle Issue. Includi:
*   Versione App (vedi `/health` o Splash Screen).
*   Log (`%LOCALAPPDATA%/Intelleo/logs/intelleo.log`).
*   Step di riproduzione.

## 3. Pull Requests

1.  Forka il repo (se esterno) o crea un branch `feat/` (se interno).
2.  Aggiungi test per la nuova funzionalità.
3.  Aggiorna la documentazione in `docs/` se cambi logica core.
4.  Attendi la Code Review.

## 4. Note Legali
Ogni contributo al codice diventa proprietà esclusiva dell'azienda titolare del progetto Intelleo.
