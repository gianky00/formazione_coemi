@echo off

REM --- 1. Controlla e Crea l'Ambiente Virtuale ---
echo Checking for virtual environment...
IF NOT EXIST ".\Scripts\activate.bat" (
    echo Creating virtual environment with Python 3.12...
    py -3.12 -m venv .
)

REM --- 2. ATTIVA L'AMBIENTE VIRTUALE ---
echo Activating virtual environment...
CALL .\Scripts\activate

REM --- 3. Installa Dipendenze Python ---
echo Ensuring pip is installed...
python -m pip install --upgrade pip

echo Installing dependencies from requirements.txt...
python -m pip install -r requirements.txt

REM --- 4. Installa Dipendenze Playwright ---
echo Installing Playwright dependencies...
playwright install --with-deps

REM --- 5. Avvia le Applicazioni ---
echo Starting the backend server...
set PYTHONPATH=.
start /b python app/main.py

echo Starting the application...
python desktop_app/main.py

pause