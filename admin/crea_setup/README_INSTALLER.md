# Creazione Installer Intelleo

Guida per la creazione dell'installer Windows usando Inno Setup.

---

## Prerequisiti

### Software Richiesto

1. **Inno Setup 6.2+**
   - Download: https://jrsoftware.org/isdl.php
   - Installa in `C:\Program Files (x86)\Inno Setup 6\`

2. **Build Nuitka completato**
   ```
   dist/nuitka/Intelleo.dist/Intelleo.exe
   ```

### Verifica Prerequisiti

```bash
# Verifica Inno Setup installato
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /?

# Verifica build Nuitka esiste
dir dist\nuitka\Intelleo.dist\Intelleo.exe
```

---

## Procedura Build Installer

### Metodo 1: Command Line (Raccomandato)

```bash
cd admin/crea_setup
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" setup_script.iss
```

### Metodo 2: GUI

1. Apri `setup_script.iss` con Inno Setup Compiler (doppio click)
2. Menu `Build` → `Compile` (o premi `F9`)
3. Attendi completamento

### Output

```
dist/installer/Intelleo_Setup_v2.0.0.exe
```

---

## Parametri Custom

### Specificare Versione

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /dMyAppVersion=2.1.0 setup_script.iss
```

### Specificare Build Directory

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" /dBuildDir=C:\path\to\build setup_script.iss
```

---

## Struttura Output Attesa

```
dist/
├── installer/
│   └── Intelleo_Setup_v2.0.0.exe    (~150 MB)
└── nuitka/
    └── Intelleo.dist/
        ├── Intelleo.exe
        ├── guide/
        ├── desktop_app/
        └── ...
```

---

## Test Pre-Distribuzione

### Ambiente di Test

Testare su macchina **pulita** (senza Python, senza Intelleo):
- Windows 10 VM
- Windows 11 VM
- Windows Sandbox (Windows 10 Pro+)

### Checklist Test

#### Durante Installazione
- [ ] Wizard si apre correttamente
- [ ] UAC prompt appare (richiede admin)
- [ ] Directory default: `C:\Program Files\Intelleo`
- [ ] Progress bar funziona
- [ ] Nessun errore di copia file
- [ ] Shortcuts creati (Desktop opzionale, Start Menu)

#### Post-Installazione
- [ ] Cartella installazione: ~150-200 MB
- [ ] `Intelleo.exe` esiste
- [ ] Cartella `guide/` esiste con `index.html`
- [ ] Uninstaller in Control Panel

#### Avvio Applicazione
- [ ] Doppio click shortcut funziona
- [ ] App si avvia in <5 secondi
- [ ] Splash screen appare
- [ ] Login screen visibile
- [ ] NO errori "DLL not found"
- [ ] NO errori "Module not found"

---

## Troubleshooting

### "Source file not found"

**Causa**: Build Nuitka non presente.

**Soluzione**:
```bash
python admin/offusca/build_nuitka.py --clean
```

### "vcruntime140.dll not found" su test machine

**Causa**: Mancano Visual C++ Redistributables.

**Soluzioni**:
1. L'utente installa VC++ Redist da Microsoft
2. O includi `vc_redist.x64.exe` nell'installer (vedi sezione avanzata in `setup_script.iss`)

### Installer troppo grande (>300 MB)

**Verifica**: La compressione è attiva in `setup_script.iss`:
```ini
Compression=lzma2/ultra64
SolidCompression=yes
```

---

## Distribuzione

### Generare Checksum

```bash
certutil -hashfile dist\installer\Intelleo_Setup_v2.0.0.exe SHA256
```

### Canali Distribuzione

1. **Server aziendale** (raccomandato)
2. **Cloud storage** (Google Drive, Dropbox)
3. **GitHub Releases** (per repo privati)

### Release Notes Template

```markdown
## Intelleo v2.0.0

### Novità
- Build con Nuitka (performance migliorate)
- Avvio più veloce (~40% più rapido)
- Protezione IP migliorata

### Requisiti
- Windows 10/11 (64-bit)
- 4 GB RAM
- 500 MB spazio disco

### Download
- Installer: Intelleo_Setup_v2.0.0.exe
- SHA256: [checksum]

### Note Installazione
Al primo avvio, inserire la licenza fornita.
```

---

## File Correlati

| File | Descrizione |
|------|-------------|
| `setup_script.iss` | Script Inno Setup principale |
| `EULA.rtf` | Contratto di licenza (visualizzato durante setup) |
| `../../desktop_app/assets/installer_wizard.bmp` | Immagine wizard (164x314 px) |
| `../../desktop_app/assets/installer_small.bmp` | Logo piccolo (55x58 px) |
| `../../desktop_app/icons/icon.ico` | Icona applicazione |

---

**Ultima modifica**: 2024-12-10
**Versione script**: 2.0.0 (Nuitka)
