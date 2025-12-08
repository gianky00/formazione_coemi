@echo off
:: Disabilita l'eco dei comandi per pulizia
cls

echo.
echo ========================================================
echo  DEBUG MODE: PULIZIA BRANCH
echo ========================================================
echo.
echo 1. Verifica presenza GIT...

git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRORE] Git non trovato o non nel PATH.
    echo Installa Git per Windows e riprova.
    pause
    exit /b
)
echo    [OK] Git trovato.

echo.
echo 2. Aggiornamento lista remota (git fetch -p)...
git fetch -p
if %errorlevel% neq 0 (
    echo [ERRORE] Impossibile contattare il repository remoto.
    echo Verifica la connessione internet.
    pause
    exit /b
)
echo    [OK] Fetch completato.

echo.
echo 3. Creazione lista branch da eliminare...
:: Scriviamo su file temporaneo per evitare errori di memoria
:: Escludiamo "main" e "HEAD" in modo sicuro
git branch -r > tutti_branch.tmp
findstr /v "main" tutti_branch.tmp | findstr /v "HEAD" > da_cancellare.tmp

:: Contiamo le righe (se il file è vuoto o ha 0 righe)
for %%A in (da_cancellare.tmp) do if %%~zA==0 goto :NESSUN_BRANCH

echo.
echo --------------------------------------------------------
echo  ATTENZIONE: STO PER CANCELLARE QUESTI BRANCH:
echo --------------------------------------------------------
type da_cancellare.tmp
echo --------------------------------------------------------
echo.

:CHIEDI_CONFERMA
set /p "risposta=Scrivi DISTRUGGI per confermare (o premi invio per uscire): "
if not "%risposta%"=="DISTRUGGI" goto :ANNULLA

echo.
echo ========================================================
echo  AVVIO CANCELLAZIONE...
echo ========================================================
echo.

:: Ciclo di cancellazione che legge dal file riga per riga
for /f "tokens=1,* delims=/" %%A in (da_cancellare.tmp) do call :ELIMINA_SINGOLO "%%B"

goto :FINE_SUCCESSO

:ELIMINA_SINGOLO
set "branch=%~1"
:: Rimuovi spazi eventuali
if "%branch%"=="" goto :EOF
echo Cancellazione remota di: %branch%
git push origin --delete "%branch%"
goto :EOF

:NESSUN_BRANCH
echo.
echo [INFO] Nessun branch extra trovato. Esiste solo il main?
goto :PULIZIA_FINALE

:ANNULLA
echo.
echo [INFO] Operazione ANNULLATA dall'utente.
goto :PULIZIA_FINALE

:FINE_SUCCESSO
echo.
echo [SUCCESSO] Tutti i branch elencati sono stati cancellati.

:PULIZIA_FINALE
:: Rimuove i file temporanei
if exist tutti_branch.tmp del tutti_branch.tmp
if exist da_cancellare.tmp del da_cancellare.tmp
echo.
echo Premi un tasto per chiudere...
pause >nul