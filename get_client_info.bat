@echo off
TITLE Estrazione Dati Hardware per Licenza
color 0A

echo ---------------------------------------------------
echo      ESTRAZIONE IDENTIFICATIVI HARDWARE
echo ---------------------------------------------------
echo.
echo Sto recuperando le informazioni necessarie per la tua licenza...
echo.

REM Crea un file temporaneo
set OUTFILE=info_hardware.txt

echo --- DISK SERIAL NUMBER --- > %OUTFILE%
wmic diskdrive get SerialNumber >> %OUTFILE%

echo. >> %OUTFILE%
echo --- MAC ADDRESS --- >> %OUTFILE%
getmac >> %OUTFILE%

echo.
echo Operazione completata!
echo.
echo Le seguenti informazioni sono state copiate negli appunti:
echo.
type %OUTFILE%
echo.

REM Copia tutto il contenuto del file negli appunti
type %OUTFILE% | clip

echo ---------------------------------------------------
echo ISTRUZIONI:
echo 1. Apri la tua email o chat con lo sviluppatore.
echo 2. Premi CTRL+V (Incolla) per inviare questi dati.
echo ---------------------------------------------------
echo.
pause
del %OUTFILE%
