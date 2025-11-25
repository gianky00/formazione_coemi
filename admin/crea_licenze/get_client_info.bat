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
set ERRFILE=hw_error.log

REM Esegui lo script Python unificato per ottenere l'ID, catturando l'output di errore
python "%~dp0\\..\\tools\\get_id_for_admin.py" > %OUTFILE% 2> %ERRFILE%

REM Controlla se lo script ha prodotto un errore
if %errorlevel% neq 0 (
    echo [ERRORE] Impossibile ottenere l'Hardware ID.
    echo Dettagli dell'errore:
    echo.
    type %ERRFILE%
    del %ERRFILE%
    del %OUTFILE%
    echo.
    pause
    exit /b
)

REM Controlla se il file di output e' vuoto
if not exist %OUTFILE% (
    echo [ERRORE] Il file di output non e' stato creato.
    del %ERRFILE%
    pause
    exit /b
)
for %%A in (%OUTFILE%) do if %%~zA equ 0 (
    echo [ERRORE] Lo script non ha prodotto un Hardware ID.
    del %OUTFILE%
    del %ERRFILE%
    pause
    exit /b
)


REM Leggi l'ID dal file
set /p HWID=<%OUTFILE%
del %ERRFILE%

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
