@echo off
echo Installing dependencies...
pip install -r requirements.txt

echo Starting the application...
set PYTHONPATH=.
python desktop_app/main_window.py
