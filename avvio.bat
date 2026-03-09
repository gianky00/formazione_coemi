@echo off

ECHO --- 1. Controlla e Crea l'Ambiente Virtuale ---
IF NOT EXIST ".\Scripts\activate.bat" (
    ECHO Creazione ambiente virtuale in corso...
    py -3.12 -m venv .
) ELSE (
    ECHO Ambiente virtuale trovato.
)

REM --- 2. ATTIVA L'AMBIENTE VIRTUALE ---
ECHO Attivazione ambiente virtuale...
CALL .\Scripts\activate

REM --- 3. Installa Dipendenze Python ---
ECHO Aggiornamento dipendenze...
python -m pip install -r requirements.txt > STARTUP_LOG.txt 2>&1

REM --- 4. Avvia le Applicazioni ---
ECHO Avvio applicazioni (Output in STARTUP_LOG.txt)...
set PYTHONPATH=.

REM Redirezione totale: stdout e stderr vengono scritti in STARTUP_LOG.txt
python launcher.py >> STARTUP_LOG.txt 2>&1

ECHO Esecuzione terminata. Controlla STARTUP_LOG.txt in caso di errori.
