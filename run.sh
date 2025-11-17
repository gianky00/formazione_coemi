#!/bin/bash

# --- 1. Controlla e Crea l'Ambiente Virtuale ---
echo "Checking for virtual environment..."
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment with Python 3.12..."
    python3.12 -m venv .venv
fi

# --- 2. ATTIVA L'AMBIENTE VIRTUALE ---
echo "Activating virtual environment..."
source .venv/bin/activate

# --- 3. Installa Dipendenze Python ---
echo "Ensuring pip is installed..."
python -m pip install --upgrade pip

echo "Installing dependencies from requirements.txt..."
python -m pip install -r requirements.txt

# --- 4. Installa Dipendenze Playwright ---
if ! playwright --version > /dev/null 2>&1; then
    echo "Installing Playwright dependencies..."
    playwright install --with-deps
fi

# --- 5. Avvia le Applicazioni ---
echo "Starting the backend server..."
export PYTHONPATH=.
python app/main.py &

echo "Starting the application..."
python desktop_app/main.py
