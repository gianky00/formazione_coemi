"""
Master Build Script - Nuitka Compilation Pipeline

Questo script gestisce l'intera pipeline di build per Intelleo:
1. Verifica ambiente (Python, Nuitka, MSVC, Node.js)
2. Build React frontend (guide_frontend)
3. Compilazione Nuitka (Python → C → Binary)
4. Post-processing (README, verifica output)
5. Generazione report

Usage:
    python admin/offusca/build_nuitka.py [--clean] [--fast] [--skip-checks]

Options:
    --clean        Pulisce build precedenti prima di compilare
    --fast         Build veloce (disabilita LTO, meno ottimizzato)
    --skip-checks  Salta verifica ambiente (usa con cautela)

Author: Migration Team
Version: 1.0.0 (Nuitka Migration)
"""
import subprocess
import sys
import os
import shutil
import time
from pathlib import Path
from datetime import datetime
import argparse
import logging

# =============================================================================
# CONFIGURATION
# =============================================================================

# Project paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DIST_DIR = PROJECT_ROOT / "dist" / "nuitka"
FRONTEND_DIR = PROJECT_ROOT / "guide_frontend"
ENTRY_POINT = PROJECT_ROOT / "launcher.py"
APP_NAME = "Intelleo"

# Icon path (check multiple locations)
ICON_PATHS = [
    PROJECT_ROOT / "desktop_app" / "icons" / "icon.ico",
    PROJECT_ROOT / "desktop_app" / "assets" / "logo.ico",
    PROJECT_ROOT / "desktop_app" / "assets" / "icon.png",
]

# Build log
BUILD_LOG = PROJECT_ROOT / "admin" / "offusca" / "build_nuitka_log.txt"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(BUILD_LOG, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# =============================================================================
# CONSOLE OUTPUT HELPERS
# =============================================================================

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass  # Fallback if already wrapped


def log_section(title: str):
    """Print section header."""
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")
    logger.info(f"=== {title} ===")


def log_success(msg: str):
    """Log success message."""
    print(f"✅ {msg}")
    logger.info(f"SUCCESS: {msg}")


def log_error(msg: str):
    """Log error message."""
    print(f"❌ {msg}")
    logger.error(f"ERROR: {msg}")


def log_warning(msg: str):
    """Log warning message."""
    print(f"⚠️  {msg}")
    logger.warning(f"WARNING: {msg}")


def log_info(msg: str):
    """Log info message."""
    print(f"ℹ️  {msg}")
    logger.info(msg)


# =============================================================================
# ENVIRONMENT CHECKS
# =============================================================================

def check_environment() -> bool:
    """
    Verifica che l'ambiente di build sia pronto.
    
    Checks:
    - Python 3.12+
    - Nuitka installato
    - MSVC disponibile (cl.exe)
    - Node.js + npm
    - Frontend buildato
    
    Returns:
        bool: True se tutti i check passano
    """
    log_section("🔍 VERIFICA AMBIENTE")
    
    all_pass = True
    
    # Check 1: Python version
    py_version = sys.version_info
    if py_version >= (3, 12):
        log_success(f"Python {py_version.major}.{py_version.minor}.{py_version.micro}")
    else:
        log_error(f"Python {py_version.major}.{py_version.minor} (richiesto >= 3.12)")
        all_pass = False
    
    # Check 2: Nuitka installed
    try:
        result = subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True, text=True, timeout=10
        )
        if result.returncode == 0:
            version = result.stdout.strip().split('\n')[0]
            log_success(f"Nuitka {version}")
        else:
            log_error("Nuitka non funzionante")
            all_pass = False
    except FileNotFoundError:
        log_error("Nuitka non installato. Esegui: pip install nuitka")
        all_pass = False
    except Exception as e:
        log_error(f"Errore verifica Nuitka: {e}")
        all_pass = False
    
    # Check 3: MSVC compiler (via Nuitka detection or direct)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True, text=True, timeout=15
        )
        if "Version C compiler:" in result.stdout:
            for line in result.stdout.split('\n'):
                if "Version C compiler:" in line:
                    compiler_info = line.replace("Version C compiler:", "").strip()
                    # Truncate long path
                    if len(compiler_info) > 60:
                        compiler_info = "..." + compiler_info[-57:]
                    log_success(f"MSVC: {compiler_info}")
                    break
        else:
            # Try direct cl.exe check
            cl_result = subprocess.run(["cl.exe"], capture_output=True, text=True, timeout=5)
            if "Microsoft" in cl_result.stderr:
                log_success("MSVC (cl.exe trovato)")
            else:
                log_warning("MSVC non verificato (Nuitka potrebbe trovarlo)")
    except Exception:
        log_warning("MSVC check fallito (Nuitka potrebbe comunque trovarlo)")
    
    # Check 4: Node.js + npm
    try:
        result = subprocess.run(["npm", "--version"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            log_success(f"npm {result.stdout.strip()}")
        else:
            log_error("npm non funzionante")
            all_pass = False
    except FileNotFoundError:
        log_error("npm non installato. Installa Node.js")
        all_pass = False
    except Exception as e:
        log_warning(f"Errore verifica npm: {e}")
    
    # Check 5: Frontend build
    frontend_index = FRONTEND_DIR / "dist" / "index.html"
    if frontend_index.exists():
        log_success(f"Frontend buildato ({frontend_index.relative_to(PROJECT_ROOT)})")
    else:
        log_warning("Frontend non buildato (verrà buildato automaticamente)")
    
    # Check 6: Entry point exists
    if ENTRY_POINT.exists():
        log_success(f"Entry point: {ENTRY_POINT.name}")
    else:
        log_error(f"Entry point non trovato: {ENTRY_POINT}")
        all_pass = False
    
    # Check 7: Icon exists
    icon_found = False
    for icon_path in ICON_PATHS:
        if icon_path.exists():
            log_success(f"Icon: {icon_path.relative_to(PROJECT_ROOT)}")
            icon_found = True
            break
    if not icon_found:
        log_warning("Icon non trovata (build procederà senza icona custom)")
    
    return all_pass


# =============================================================================
# BUILD STEPS
# =============================================================================

def build_frontend() -> bool:
    """
    Build React frontend se necessario.
    
    Returns:
        bool: True se frontend è pronto
    """
    log_section("⚛️  BUILD REACT FRONTEND")
    
    frontend_index = FRONTEND_DIR / "dist" / "index.html"
    
    if frontend_index.exists():
        log_success("Frontend già buildato (dist/index.html esiste)")
        return True
    
    log_info("Frontend non buildato, eseguo npm run build...")
    
    try:
        # Install dependencies first if needed
        if not (FRONTEND_DIR / "node_modules").exists():
            log_info("Installazione dipendenze npm...")
            subprocess.run(
                ["npm", "install"],
                cwd=FRONTEND_DIR,
                check=True,
                capture_output=True
            )
        
        # Build
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=FRONTEND_DIR,
            capture_output=True,
            text=True,
            check=True
        )
        
        if frontend_index.exists():
            log_success("Frontend build completato")
            return True
        else:
            log_error("Build completato ma index.html non trovato")
            return False
            
    except subprocess.CalledProcessError as e:
        log_error(f"Build frontend fallito: {e.stderr}")
        return False
    except Exception as e:
        log_error(f"Errore build frontend: {e}")
        return False


def clean_build_dir():
    """Rimuove directory di build precedenti."""
    log_section("🧹 PULIZIA")
    
    if DIST_DIR.exists():
        log_info(f"Rimuovo {DIST_DIR.relative_to(PROJECT_ROOT)}")
        try:
            shutil.rmtree(DIST_DIR)
            log_success("Directory pulita")
        except PermissionError:
            log_error("Impossibile rimuovere - file in uso. Chiudi Intelleo.exe")
            sys.exit(1)
        except Exception as e:
            log_error(f"Errore pulizia: {e}")
            sys.exit(1)
    else:
        log_info("Nessuna directory da pulire")


def get_icon_path() -> str:
    """Find the first existing icon path."""
    for icon_path in ICON_PATHS:
        if icon_path.exists():
            return str(icon_path)
    return ""


def get_nuitka_command(fast_mode: bool = False) -> list:
    """
    Costruisce il comando Nuitka completo.
    
    Args:
        fast_mode: Se True, disabilita LTO per build più veloce
    
    Returns:
        list: Lista di argomenti per subprocess
    """
    cmd = [
        sys.executable, "-m", "nuitka",
        
        # === MODALITÀ STANDALONE ===
        "--standalone",
        "--assume-yes-for-downloads",
        
        # === PLUGINS ESSENZIALI ===
        "--plugin-enable=pyqt6",
        "--plugin-enable=numpy",
        "--enable-plugin=multiprocessing",
        
        # === INCLUSIONE DATI ===
        # React SPA (guide)
        f"--include-data-dir={FRONTEND_DIR / 'dist'}=guide",
        # Assets desktop app
        f"--include-data-dir={PROJECT_ROOT / 'desktop_app' / 'assets'}=desktop_app/assets",
        f"--include-data-dir={PROJECT_ROOT / 'desktop_app' / 'icons'}=desktop_app/icons",
        # Docs (per LYRA profile)
        f"--include-data-files={PROJECT_ROOT / 'docs' / 'LYRA_PROFILE.md'}=docs/LYRA_PROFILE.md",
        
        # === PACKAGES COMPLETI ===
        "--include-package=app",
        "--include-package=desktop_app",
        
        # === MODULI CRITICI (Import dinamici) ===
        # Backend
        "--include-module=uvicorn",
        "--include-module=uvicorn.logging",
        "--include-module=uvicorn.loops",
        "--include-module=uvicorn.loops.auto",
        "--include-module=uvicorn.protocols",
        "--include-module=uvicorn.protocols.http",
        "--include-module=uvicorn.protocols.http.auto",
        "--include-module=uvicorn.lifespan",
        "--include-module=uvicorn.lifespan.on",
        "--include-module=fastapi",
        "--include-module=starlette",
        "--include-module=pydantic",
        "--include-module=pydantic_settings",
        
        # Database
        "--include-module=sqlalchemy",
        "--include-module=sqlalchemy.sql.default_comparator",
        "--include-module=sqlalchemy.dialects.sqlite",
        
        # AI & APIs
        "--include-module=google.generativeai",
        "--include-module=google.api_core",
        "--include-module=google.auth",
        "--include-module=google.protobuf",
        "--include-module=grpc",
        "--include-module=httpx",
        
        # Security
        "--include-module=bcrypt",
        "--include-module=cryptography",
        "--include-module=cryptography.fernet",
        "--include-module=cryptography.hazmat.backends.openssl",
        "--include-module=passlib",
        "--include-module=passlib.handlers.bcrypt",
        "--include-module=jose",
        "--include-module=jose.backends.cryptography_backend",
        
        # Utils
        "--include-module=tenacity",
        "--include-module=fpdf2",
        "--include-module=fpdf",
        "--include-module=apscheduler",
        "--include-module=pandas",
        "--include-module=numpy",
        
        # PyQt6 (oltre al plugin)
        "--include-module=PyQt6.QtSvg",
        "--include-module=PyQt6.QtNetwork",
        "--include-module=PyQt6.QtPrintSupport",
        "--include-module=PyQt6.QtWebEngineWidgets",
        "--include-module=PyQt6.QtWebEngineCore",
        "--include-module=PyQt6.QtWebChannel",
        
        # Multipart (form upload)
        "--include-module=multipart",
        "--include-module=python_multipart",
        
        # Email
        "--include-module=email.mime.text",
        "--include-module=email.mime.multipart",
        "--include-module=email.mime.application",
        
        # Sentry & Analytics
        "--include-module=sentry_sdk",
        "--include-module=posthog",
        
        # Charset
        "--include-module=charset_normalizer",
        "--include-module=charset_normalizer.md",
        
        # GeoIP & User Agents
        "--include-module=geoip2",
        "--include-module=user_agents",
        "--include-module=ua_parser",
        
        # Win32
        "--include-module=win32com.client",
        "--include-module=pythoncom",
        "--include-module=win32api",
        "--include-module=pywintypes",
        
        # === OTTIMIZZAZIONI ===
        f"--lto={'yes' if not fast_mode else 'no'}",
        
        # === PARALLELIZZAZIONE ===
        f"--jobs={os.cpu_count() or 4}",
        
        # === WINDOWS SPECIFICO ===
        "--windows-disable-console",
        
        # === OUTPUT ===
        f"--output-dir={DIST_DIR}",
        f"--output-filename={APP_NAME}.exe",
    ]
    
    # Add icon if exists
    icon_path = get_icon_path()
    if icon_path:
        cmd.append(f"--windows-icon-from-ico={icon_path}")
    
    # Entry point (MUST be last)
    cmd.append(str(ENTRY_POINT))
    
    return cmd


def compile_with_nuitka(fast_mode: bool = False) -> bool:
    """
    Esegue compilazione Nuitka con output real-time.
    
    La compilazione Nuitka avviene in più fasi:
    1. Python Analysis (~5-10 min prima volta)
    2. C Code Generation (~2-5 min)
    3. C Compilation (~20-30 min prima volta)
    4. Linking (~2-5 min)
    
    Args:
        fast_mode: Se True, disabilita LTO per build più veloce
    
    Returns:
        bool: True se compilazione riuscita
    """
    log_section("🚀 COMPILAZIONE NUITKA")
    
    if fast_mode:
        log_warning("Modalità FAST: LTO disabilitato (build più veloce ma meno ottimizzato)")
    
    cmd = get_nuitka_command(fast_mode)
    
    # Log comando completo (formattato per leggibilità)
    print("🔧 Comando Nuitka:")
    print("  " + " \\\n    ".join(cmd[:5]) + " \\")
    print(f"    ... (+{len(cmd)-6} parametri) ...")
    print(f"    {cmd[-1]}")
    print()
    
    print("⏳ Inizio compilazione...")
    print("   📊 Prima build: ~35-50 minuti")
    print("   📊 Build successive (con ccache): ~10-15 minuti")
    print("   💡 Tip: Installa ccache per velocizzare: choco install ccache")
    print()
    print("-" * 70)
    print("  OUTPUT NUITKA (real-time)")
    print("-" * 70)
    
    start_time = time.time()
    
    # Real-time output con Popen
    try:
        process = subprocess.Popen(
            cmd,
            cwd=PROJECT_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
            universal_newlines=True
        )
        
        # Stampa output in real-time
        for line in process.stdout:
            # Flush per garantire output immediato
            print(line, end='', flush=True)
            # Log to file (senza newline perché già presente)
            logger.info(f"[NUITKA] {line.rstrip()}")
        
        process.wait()
        elapsed = time.time() - start_time
        elapsed_min = elapsed / 60
        
        print("-" * 70)
        
        if process.returncode == 0:
            log_success(f"Compilazione completata in {elapsed_min:.1f} minuti")
            
            # Verifica output eseguibile
            exe_path = DIST_DIR / f"{APP_NAME}.dist" / f"{APP_NAME}.exe"
            if exe_path.exists():
                size_mb = exe_path.stat().st_size / (1024 * 1024)
                log_success(f"Eseguibile: {exe_path.relative_to(PROJECT_ROOT)} ({size_mb:.1f} MB)")
                return True
            else:
                # Try alternate paths
                alt_paths = [
                    DIST_DIR / f"{APP_NAME}.exe",
                    DIST_DIR / "launcher.dist" / f"{APP_NAME}.exe",
                    DIST_DIR / "launcher.dist" / "launcher.exe",
                ]
                for alt_exe in alt_paths:
                    if alt_exe.exists():
                        size_mb = alt_exe.stat().st_size / (1024 * 1024)
                        log_success(f"Eseguibile (path alternativo): {alt_exe} ({size_mb:.1f} MB)")
                        return True
                
                log_error(f"Eseguibile non trovato in: {exe_path}")
                log_info("Cerco in directory dist...")
                # List what's in dist
                if DIST_DIR.exists():
                    for item in DIST_DIR.iterdir():
                        print(f"  - {item.name}")
                return False
        else:
            log_error(f"Compilazione fallita dopo {elapsed_min:.1f} minuti")
            log_error(f"Exit code: {process.returncode}")
            return False
            
    except KeyboardInterrupt:
        log_warning("Compilazione interrotta dall'utente (Ctrl+C)")
        if 'process' in locals():
            process.terminate()
            process.wait(timeout=5)
        return False
    except Exception as e:
        log_error(f"Errore durante compilazione: {e}")
        return False
            
    except subprocess.TimeoutExpired:
        log_error("Compilazione timeout (>2 ore)")
        return False
    except Exception as e:
        log_error(f"Errore compilazione: {e}")
        return False


def post_process() -> bool:
    """
    Post-processing: verifica output e crea file aggiuntivi.
    
    Returns:
        bool: True se post-processing riuscito
    """
    log_section("🔧 POST-PROCESSING")
    
    dist_root = DIST_DIR / f"{APP_NAME}.dist"
    
    # Check alternate location
    if not dist_root.exists():
        dist_root = DIST_DIR
    
    if not dist_root.exists():
        log_error(f"Directory dist non trovata: {dist_root}")
        return False
    
    # Find exe
    exe_path = dist_root / f"{APP_NAME}.exe"
    if not exe_path.exists():
        # Search recursively
        exe_files = list(dist_root.rglob(f"{APP_NAME}.exe"))
        if exe_files:
            exe_path = exe_files[0]
            dist_root = exe_path.parent
        else:
            log_error(f"Eseguibile non trovato in {dist_root}")
            return False
    
    log_success(f"Eseguibile trovato: {exe_path.relative_to(PROJECT_ROOT)}")
    
    # Create README
    readme_content = f"""Intelleo - Gestione Sicurezza sul Lavoro
==========================================

Versione: 2.0.0 (Nuitka Build)
Data Build: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

INSTALLAZIONE
-------------
1. Copia l'intera cartella in una posizione permanente
   (es: C:\\Program Files\\Intelleo)

2. Esegui {APP_NAME}.exe

3. Al primo avvio, l'app richiedera la licenza.
   Segui le istruzioni a schermo.

LICENZA
-------
La licenza deve essere posizionata in:
  %LOCALAPPDATA%\\Intelleo\\Licenza\\

Contiene 3 file:
  - pyarmor.rkey
  - config.dat
  - manifest.json

REQUISITI SISTEMA
-----------------
- Windows 10/11 (64-bit)
- 4 GB RAM minimo
- 500 MB spazio disco

SUPPORTO
--------
Per assistenza, contatta: support@intelleo.it

(c) {datetime.now().year} Intelleo. Tutti i diritti riservati.
"""
    
    readme_path = dist_root / "README.txt"
    readme_path.write_text(readme_content, encoding='utf-8')
    log_success(f"README creato: {readme_path.name}")
    
    # Copy DLLs if needed
    dll_source = PROJECT_ROOT / "dll"
    if dll_source.exists():
        dll_dest = dist_root / "dll"
        if not dll_dest.exists():
            shutil.copytree(dll_source, dll_dest)
            log_success("DLL directory copiata")
    
    # Copy license placeholder
    lic_dest = dist_root / "Licenza"
    lic_dest.mkdir(exist_ok=True)
    log_info(f"Directory Licenza creata: {lic_dest.name}")
    
    log_success("Post-processing completato")
    return True


def generate_report(start_time: float, success: bool):
    """
    Genera report finale del build.
    
    Args:
        start_time: Timestamp inizio build
        success: True se build riuscito
    """
    log_section("📊 REPORT BUILD")
    
    elapsed = time.time() - start_time
    elapsed_min = elapsed / 60
    
    print(f"Tempo totale: {elapsed_min:.1f} minuti")
    print(f"Status: {'✅ SUCCESS' if success else '❌ FAILED'}")
    
    if success:
        # Find exe
        exe_path = None
        for candidate in [
            DIST_DIR / f"{APP_NAME}.dist" / f"{APP_NAME}.exe",
            DIST_DIR / f"{APP_NAME}.exe",
        ]:
            if candidate.exists():
                exe_path = candidate
                break
        
        if exe_path:
            size_mb = exe_path.stat().st_size / (1024 * 1024)
            print(f"Eseguibile: {exe_path}")
            print(f"Dimensione: {size_mb:.1f} MB")
            
            # Count files
            dist_root = exe_path.parent
            all_files = list(dist_root.rglob("*"))
            file_count = len([f for f in all_files if f.is_file()])
            dir_count = len([f for f in all_files if f.is_dir()])
            print(f"File totali: {file_count}")
            print(f"Directory: {dir_count}")
        
        print()
        log_success("Build completato con successo! 🎉")
        print("\nProssimi passi:")
        print("  1. Testa l'eseguibile: python admin/tools/test_build.py")
        print("  2. Security audit: python admin/tools/security_audit.py dist/nuitka/...")
        print("  3. Test manuale: lancia Intelleo.exe e verifica funzionalità")
    else:
        log_error("Build fallito. Controlla gli errori sopra.")
        print("\n💡 Troubleshooting:")
        print("  - Verifica MSVC: python -m nuitka --version")
        print("  - Verifica dipendenze: pip install -r requirements.txt")
        print("  - Controlla log: admin/offusca/build_nuitka_log.txt")
        print("  - Prova modalità fast: --fast")


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Entry point principale."""
    parser = argparse.ArgumentParser(
        description="Build Intelleo con Nuitka",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python build_nuitka.py              # Build standard
  python build_nuitka.py --clean      # Pulisce e rebuilda
  python build_nuitka.py --fast       # Build veloce (no LTO)
  python build_nuitka.py --clean --fast  # Pulisce + build veloce
        """
    )
    parser.add_argument(
        "--clean", 
        action="store_true", 
        help="Pulisce build precedenti"
    )
    parser.add_argument(
        "--fast", 
        action="store_true", 
        help="Build veloce (disabilita LTO)"
    )
    parser.add_argument(
        "--skip-checks", 
        action="store_true", 
        help="Salta verifica ambiente"
    )
    args = parser.parse_args()
    
    # Header
    print(f"\n{'='*70}")
    print(f"  🏗️  INTELLEO - NUITKA BUILD PIPELINE")
    print(f"{'='*70}")
    print(f"Build iniziato: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Project root: {PROJECT_ROOT}")
    print()
    
    start_time = time.time()
    
    # Step 1: Verifica ambiente
    if not args.skip_checks:
        if not check_environment():
            log_error("Ambiente non pronto. Correggi gli errori e riprova.")
            sys.exit(1)
    else:
        log_warning("Verifica ambiente saltata (--skip-checks)")
    
    # Step 2: Clean (opzionale)
    if args.clean:
        clean_build_dir()
    
    # Step 3: Build frontend
    if not build_frontend():
        log_error("Build frontend fallito")
        generate_report(start_time, success=False)
        sys.exit(1)
    
    # Step 4: Compilazione Nuitka (MAIN)
    if not compile_with_nuitka(fast_mode=args.fast):
        generate_report(start_time, success=False)
        sys.exit(1)
    
    # Step 5: Post-processing
    if not post_process():
        log_error("Post-processing fallito")
        generate_report(start_time, success=False)
        sys.exit(1)
    
    # Step 6: Report finale
    generate_report(start_time, success=True)
    sys.exit(0)


if __name__ == "__main__":
    main()

