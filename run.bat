@echo off

REM --- ATTIVA L'AMBIENTE VIRTUALE ---
echo Activating virtual environment...
CALL .\formazione_coemi\Scripts\activate

REM --- Ora tutti i comandi 'python' e 'pip' useranno l'ambiente ---

echo Ensuring pip is installed...
python -m pip install --upgrade pip

echo Installing dependencies...
python -m pip install -r requirements.txt

echo Installing Playwright dependencies...
playwright install --with-deps

echo Starting the backend server...
set PYTHONPATH=.
start /b python app/main.py

echo Starting the application...
python desktop_app/main_window.py
pause