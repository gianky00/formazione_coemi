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
ECHO Aggiornamento pip...
python -m pip install --upgrade pip
ECHO Installazione requirements.txt...
python -m pip install -r requirements.txt

REM --- 4. Avvia le Applicazioni ---
ECHO Avvio applicazioni...
set PYTHONPATH=.

ECHO Avvio backend (output in questa finestra)...
start /b python app/main.py

ECHO Avvio desktop app (output in questa finestra)...
python -m desktop_app.main

ECHO Script terminato.
pause
