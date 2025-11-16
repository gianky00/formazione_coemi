@echo off
ECHO Questo script terminera' tutti i processi Python, pulira' l'ambiente virtuale
ECHO e riavviera' l'applicazione.
ECHO.
CHOICE /C YN /M "Sei sicuro di voler continuare?"
IF ERRORLEVEL 2 GOTO End
IF ERRORLEVEL 1 GOTO Continue

:Continue
ECHO.
ECHO --- 1. Terminazione dei processi Python in esecuzione ---
taskkill /F /IM python.exe /T > nul
ECHO Processi terminati.
ECHO.

ECHO --- 2. Pulizia dell'ambiente virtuale esistente ---
IF EXIST "Lib" (
    ECHO Rimozione della cartella 'Lib'...
    RMDIR /S /Q Lib
)
IF EXIST "Scripts" (
    ECHO Rimozione della cartella 'Scripts'...
    RMDIR /S /Q Scripts
)
IF EXIST "Include" (
    ECHO Rimozione della cartella 'Include'...
    RMDIR /S /Q Include
)
IF EXIST "pyvenv.cfg" (
    ECHO Rimozione del file 'pyvenv.cfg'...
    DEL /F /Q pyvenv.cfg
)
ECHO Pulizia completata.
ECHO.

ECHO --- 3. Riavvio dell'applicazione tramite avvio.bat ---
CALL avvio.bat

:End
ECHO Operazione annullata.
pause
