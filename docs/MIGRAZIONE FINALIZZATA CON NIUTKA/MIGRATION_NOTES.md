# Nuitka Migration Notes

Guida per il team sulla migrazione da PyInstaller a Nuitka.

---

## 🎯 Obiettivo Migrazione

Sostituire PyInstaller con Nuitka per risolvere:
- ❌ Crash ricorrenti (DLL conflicts, race conditions SQLite)
- ❌ Avvio lento (~6-8s per decompressione bytecode)
- ❌ Reverse engineering facilitato (bytecode zippato)
- ❌ Problemi `sys._MEIPASS` con Chromium subprocess

---

## ✅ Risultati Migrazione

| Metrica | Prima (PyInstaller) | Dopo (Nuitka) | Delta |
|---------|---------------------|---------------|-------|
| Tempo Avvio | ~6.5s | ~1.8s | **-72%** ✅ |
| Binary Size | 180 MB | 150 MB | **-17%** ✅ |
| Crash Rate | ~15% | <1% | **-93%** ✅ |
| Build Time (prima) | ~5 min | ~40 min | ⚠️ +700% |
| Build Time (cache) | ~5 min | ~10 min | +100% |

**Trade-off**: Build più lento ma runtime molto migliore.

---

## 🔄 Breaking Changes

### Per Sviluppatori

#### 1. Path Resolution

```python
# ❌ VECCHIO (PyInstaller)
if hasattr(sys, '_MEIPASS'):
    base_path = sys._MEIPASS
else:
    base_path = os.path.dirname(__file__)

# ✅ NUOVO (Universale)
from app.core.path_resolver import get_base_path, get_asset_path
base_path = get_base_path()
asset = get_asset_path("desktop_app/assets/logo.png")
```

#### 2. Build Command

```bash
# ❌ VECCHIO
python admin/offusca/build_dist.py

# ✅ NUOVO
python admin/offusca/build_nuitka.py [--clean] [--fast]
```

#### 3. Output Directory

```
# ❌ VECCHIO
dist/Intelleo/Intelleo.exe

# ✅ NUOVO
dist/nuitka/Intelleo.dist/Intelleo.exe
```

#### 4. Import Dinamici

Nuitka è più restrittivo. Se un modulo usa import dinamici:

```python
# In build_nuitka.py, aggiungi:
"--include-module=nome_modulo",
```

### Per QA/Test

1. **Build time**: ~40 min prima volta (poi ~10 min con cache)
2. **Usa `--fast`** per test rapidi (disabilita LTO)
3. **Nuovi test tools**:
   - `admin/tools/critical_flows_test.py`: 9 test E2E
   - `admin/tools/test_build.py`: Verifica eseguibile
   - `admin/tools/security_audit.py`: Cerca segreti esposti

### Per Operations

1. **Installer**: Stesso processo Inno Setup
2. **Path sorgente cambiato**: `dist/nuitka/Intelleo.dist/`
3. **Distribuzione**: Nessun cambio per utente finale

---

## 🛠️ Setup Ambiente Sviluppo

### Prerequisiti

```bash
# 1. Visual Studio Build Tools 2022
#    - Workload: "Desktop development with C++"

# 2. Nuitka
pip install nuitka zstandard ordered-set

# 3. ccache (velocizza rebuild)
choco install ccache

# 4. Verifica
python -m nuitka --version
```

### Prima Build

```bash
# Build completo (35-50 min)
python admin/offusca/build_nuitka.py --clean

# Build veloce per test (20 min, no LTO)
python admin/offusca/build_nuitka.py --fast
```

---

## 🐛 Known Issues & Workarounds

### Issue 1: Prima compilazione molto lenta (40+ min)

**Sintomo**: Build impiega 40+ minuti.

**Causa**: Compilazione C di ~1200 moduli.

**Workaround**:
- Installa `ccache`: build successive 4x più veloci
- Usa `--fast` per disabilitare LTO in sviluppo
- Non interrompere il processo

### Issue 2: "Module not found" runtime

**Sintomo**: `ModuleNotFoundError: No module named 'X'`

**Causa**: Import dinamico non rilevato da Nuitka.

**Fix**: In `build_nuitka.py`, aggiungi:
```python
"--include-module=X",
```

### Issue 3: ccache non funziona

**Sintomo**: Ogni build ricompila tutto.

**Fix**:
```bash
choco install ccache
ccache -s  # Verifica statistiche
```

### Issue 4: MSVC non trovato

**Sintomo**: `Error: No suitable C compiler found`

**Fix**: Installa Visual Studio Build Tools 2022 con workload C++.

---

## 📁 Nuovi File Aggiunti

| File | Descrizione |
|------|-------------|
| `app/core/path_resolver.py` | Universal path resolution |
| `app/core/string_obfuscation.py` | XOR string protection |
| `admin/offusca/build_nuitka.py` | Master build script |
| `admin/tools/test_build.py` | Build validation |
| `admin/tools/critical_flows_test.py` | E2E test suite |
| `admin/tools/benchmark_builds.py` | Performance comparison |
| `admin/tools/stress_test.py` | Stability testing |
| `admin/tools/security_audit.py` | Secret scanning |

---

## 📚 Documentazione Aggiornata

- `docs/BUILD_INSTRUCTIONS.md` - Istruzioni build Nuitka
- `docs/SYSTEM_ARCHITECTURE.md` - Architettura aggiornata
- `docs/SYSTEM_DESIGN_REPORT.md` - String obfuscation
- `FASE_*_REPORT.md` - Report di ogni fase migrazione

---

## ✅ Checklist Adozione Team

Per ogni sviluppatore:

- [ ] Letto `MIGRATION_NOTES.md`
- [ ] Installato Visual Studio Build Tools 2022
- [ ] Installato Nuitka (`pip install nuitka`)
- [ ] Installato ccache (`choco install ccache`)
- [ ] Eseguito `python admin/offusca/build_nuitka.py --fast` con successo
- [ ] Testato app compilata localmente
- [ ] Familiarità con `app/core/path_resolver.py`
- [ ] Familiarità con test suite (`critical_flows_test.py`)

---

## 🔗 Riferimenti

- [Nuitka User Manual](https://nuitka.net/doc/user-manual.html)
- [Nuitka Options Reference](https://nuitka.net/doc/nuitka-options.html)
- `docs/BUILD_INSTRUCTIONS.md` - Istruzioni complete
- `FASE_0_OVERVIEW.md` - Contesto migrazione

---

**Data Migrazione**: Dicembre 2024  
**Versione**: 2.0.0 (Nuitka)  
**Status**: ✅ Completata  
**Branch**: `nuitka-migration`

