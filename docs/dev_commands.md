# Guida Comandi Sviluppo

In questo documento sono raccolti i comandi principali per il testing, la copertura e il build del progetto.

## Testing con Pytest

### Esecuzione Standard
```powershell
.\Scripts\activate
python -m pytest tests
```

### Analisi Copertura (Coverage)
```powershell
.\Scripts\activate
python -m pytest --cov=. --cov-report=xml:reports/coverage.xml --cov-report=term-missing
```

### Generazione Report JUnit (per Sonar)
```powershell
.\Scripts\activate
python -m pytest tests --junitxml=reports/junit.xml
```

---

## Tool e Build

### Generazione Guida (Node.js richiesta)
```powershell
# Installazione Node.js se mancante
winget install OpenJS.NodeJS

.\Scripts\activate
python tools/build_guide.py
```

### Offuscamento e Build con Nuitka
```powershell
.\Scripts\activate
# Build standard
python admin/offusca/build_nuitka.py

# Build veloce con pulizia
python admin/offusca/build_nuitka.py --fast --clean
```

---

## Operazioni Git (Reset & Push)
```powershell
git init
git branch -M main
git remote remove origin
git remote add origin https://github.com/gianky00/formazione_coemi.git
git add .
git commit -m "Versione da cartella locale"
git push -u origin main --force
```

---

## Statistiche Codice (LOC) - PowerShell
Esegui questo comando in PowerShell dalla root del progetto per calcolare le Righe di Codice (escludendo commenti e file generati):

```powershell
$files = Get-ChildItem -Recurse -File "." | Where-Object { ($_.FullName -notmatch '\\(\.git|\.pytest_cache|__pycache__|venv|\.venv|env|Lib|Scripts|Include|site-packages|node_modules|build|dist|tests|test|migrations)\\') -and ($_.Extension -match '^\.(py|js|jsx|ts|tsx|html|css|qml|iss|bat|ps1|sh)$') -and ($_.Name -ne '__init__.py') -and ($_.Name -notmatch '\.min\.') }; $LOC = 0; foreach ($f in $files) { $lines = Get-Content $f.FullName | Where-Object { $t = $_.Trim(); $t -ne "" -and -not ($t.StartsWith("#") -and ($f.Extension -match "\.(py|ps1|sh)")) -and -not ($t.StartsWith("//") -and ($f.Extension -match "\.(js|jsx|ts|tsx|qml)")) -and -not (($t.StartsWith("REM") -or $t.StartsWith("::")) -and $f.Extension -eq ".bat") }; $LOC += @($lines).Count }; Write-Host "File Codice: $($files.Count)"; Write-Host "Righe Codice Puro: $LOC"
```
