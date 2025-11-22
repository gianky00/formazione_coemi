@echo off
TITLE Recupero Seriale Disco - Coemi
color 1F
cls

echo ========================================================
echo    RECUPERO SERIALE FISICO DISCO (LICENZA)
echo ========================================================
echo.
echo Attendi qualche secondo...
echo.

REM File di output
set OUTFILE=seriale_disco.txt

REM Comando PowerShell robusto per prendere il seriale fisico
powershell -Command "Get-CimInstance Win32_DiskDrive | Select-Object -First 1 -ExpandProperty SerialNumber" > %OUTFILE%

echo.
echo ========================================================
echo    OPERAZIONE COMPLETATA!
echo ========================================================
echo.
echo Il seriale e' stato salvato nel file: %OUTFILE%
echo.
echo Il contenuto e' stato copiato negli appunti.
echo Premi CTRL+V nella mail/chat per inviarlo.
echo.

REM Copia negli appunti pulendo gli spazi vuoti
powershell -Command "(Get-Content %OUTFILE%).Trim()" | clip

pause