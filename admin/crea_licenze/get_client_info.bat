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

REM Verifica se python e pyarmor sono installati
python -m pyarmor.cli --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRORE] Python o PyArmor non sembrano installati o
    echo configurati correttamente nel PATH di sistema.
    echo.
    echo Assicurarsi di aver installato Python e poi eseguire:
    echo pip install pyarmor
    echo.
    pause
    exit /b
)

echo Ottenimento dell'ID in corso...
echo.

REM File di output
set OUTFILE=hardware_id.txt

REM Comando PyArmor per ottenere l'harddisk serial number
python -m pyarmor.cli hdinfo | findstr "Harddisk serial number" > %OUTFILE%

REM Estrai solo l'ID dal file
for /f "tokens=5" %%i in (%OUTFILE%) do set HWID=%%i

echo %HWID% > %OUTFILE%

echo.
echo ========================================================
echo    OPERAZIONE COMPLETATA!
echo ========================================================
echo.
echo L'Hardware ID e' stato salvato nel file: %OUTFILE%
echo Il valore e' stato copiato automaticamente negli appunti.
echo.
echo Incolla (CTRL+V) questo ID quando richiesto dal gestore.
echo.

REM Copia l'ID pulito negli appunti
clip < %OUTFILE%

pause
