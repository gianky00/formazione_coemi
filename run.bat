@echo off
echo Ensuring pip is installed...
py -m ensurepip --upgrade

echo Installing dependencies...
py -m pip install -r requirements.txt

echo Starting the application...
set PYTHONPATH=.
py desktop_app/main_window.py
pause