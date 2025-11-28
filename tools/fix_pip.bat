@echo off
echo Attempting to repair PIP...
python -m ensurepip --default-pip
python -m pip install --upgrade pip
echo PIP repair complete.
pause
