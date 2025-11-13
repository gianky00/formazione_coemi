@echo off
echo Ensuring pip is installed...
py -m ensurepip --upgrade

echo Installing dependencies...
py -m pip install -r requirements.txt

echo Installing Playwright dependencies...
playwright install --with-deps

echo Starting the backend server...
set PYTHONPATH=.
start /b py app/main.py

echo Starting the application...
py desktop_app/main_window.py
pause
