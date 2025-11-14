#!/bin/bash

# Install dependencies
pip install -r requirements.txt

# Run the application
PYTHONPATH=. python3 desktop_app/main_window.py
