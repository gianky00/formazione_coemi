@echo off

REM --- 1. Controlla e Crea l'Ambiente Virtuale ---
IF NOT EXIST ".\Scripts\activate.bat" (
    py -3.12 -m venv . > nul 2>&1
)

REM --- 2. ATTIVA L'AMBIENTE VIRTUALE ---
CALL .\Scripts\activate

REM --- 3. Installa Dipendenze Python ---
python -m pip install --upgrade pip > nul 2>&1
python -m pip install -r requirements.txt > nul 2>&1

REM --- 4. Installa Dipendenze Playwright ---
playwright install --with-deps > nul 2>&1

REM --- 5. Avvia le Applicazioni ---
set PYTHONPATH=.
start /b python app/main.py > backend.log 2>&1
python desktop_app/main.py > nul 2>&1
