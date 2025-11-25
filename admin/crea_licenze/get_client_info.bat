@echo off
TITLE Recupero Hardware ID per Licenza Intelleo
color 0F
cls

echo ========================================================
echo    RECUPERO HARDWARE ID (PER LICENZA INTELLEO)
echo ========================================================
echo.
echo Questo script recupera l'ID hardware univoco necessario
echo per generare la licenza del software.
echo.

REM Assicurati che Python sia nel PATH
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRORE] Python non sembra installato o configurato
    echo correttamente nel PATH di sistema.
    echo.
    pause
    exit /b
)

echo Ottenimento dell'ID in corso...
echo.

REM File di output
set OUTFILE=hardware_id.txt

REM Esegui lo script Python unificato per ottenere l'ID
python "%~dp0\\..\\tools\\get_id_for_admin.py" > %OUTFILE% 2>nul
if %errorlevel% neq 0 (
    echo [ERRORE] Impossibile eseguire lo script per ottenere l'ID.
    echo Assicurati che le dipendenze siano installate (pip install wmi).
    echo.
    pause
    exit /b
)

REM Leggi l'ID dal file
set /p HWID=<%OUTFILE%

echo.
echo ========================================================
echo    OPERAZIONE COMPLETATA!
echo ========================================================
echo.
echo L'Hardware ID e' stato salvato nel file: %OUTFILE%
echo Il valore (%HWID%) e' stato copiato automaticamente negli appunti.
echo.
echo Incolla (CTRL+V) questo ID quando richiesto dal gestore.
echo.

REM Copia l'ID pulito negli appunti
clip < %OUTFILE%

pause
