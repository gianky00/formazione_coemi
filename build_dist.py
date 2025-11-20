import subprocess
import os
import shutil
import sys
import time
import importlib.util
import ast
import sysconfig

# --- FIX FONDAMENTALE PER CMD ---
# Forza la directory di lavoro alla cartella dove si trova questo script.
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# --------------------------------

# --- CONFIGURAZIONE ---
ENTRY_SCRIPT = "launcher.py"
APP_NAME = "Intelleo"
DIST_DIR = "dist"
OBF_DIR = os.path.join(DIST_DIR, "obfuscated")

# --- UTILITÀ DI SISTEMA ---

def run_command(cmd, cwd=None):
    """Esegue un comando shell stampandolo a video."""
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}")
        sys.exit(result.returncode)

def kill_existing_process():
    """Uccide eventuali processi 'Intelleo.exe' rimasti appesi."""
    print("--- Step 0: Cleaning active processes ---")
    try:
        subprocess.run(["taskkill", "/F", "/IM", f"{APP_NAME}.exe"], 
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        print(f"Killed active {APP_NAME}.exe instances (if any).")
        time.sleep(1)
    except Exception:
        pass

def get_std_libs():
    """Recupera la lista delle librerie standard di Python per ignorarle."""
    libs = set(sys.builtin_module_names)
    try:
        libs.update(sys.stdlib_module_names)
    except AttributeError:
        pass
    return libs

def scan_imports(source_dirs):
    """Scansiona il codice per trovare import esterni."""
    print("--- Scanning source code for imports ---")
    detected_imports = set()
    std_libs = get_std_libs()

    # Aggiungi l'entry script alla scansione
    files_to_scan = [ENTRY_SCRIPT]
    
    for source_dir in source_dirs:
        if not os.path.exists(source_dir): continue
        for root, _, files in os.walk(source_dir):
            for file in files:
                if file.endswith(".py"):
                    files_to_scan.append(os.path.join(root, file))

    for path in files_to_scan:
        try:
            with open(path, "r", encoding="utf-8") as f:
                tree = ast.parse(f.read())
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        root_pkg = alias.name.split('.')[0]
                        if root_pkg not in std_libs: detected_imports.add(root_pkg)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        root_pkg = node.module.split('.')[0]
                        if root_pkg not in std_libs: detected_imports.add(root_pkg)
        except: pass

    # Rimuovi i pacchetti interni dalla lista
    detected_imports.discard("app")
    detected_imports.discard("desktop_app")
    print(f"Auto-detected external libraries: {', '.join(sorted(detected_imports))}")
    return list(detected_imports)

def check_dependencies():
    """Verifica installazione librerie critiche basata su requirements.txt."""
    print("--- Checking Build Dependencies ---")
    required_libs = [
        ("PyInstaller", "pyinstaller"), ("pyarmor", "pyarmor"),
        ("fastapi", "fastapi"), ("uvicorn", "uvicorn"), 
        ("sqlalchemy", "sqlalchemy"), ("pandas", "pandas"), 
        ("google.generativeai", "google-generativeai"),
        ("google.cloud.aiplatform", "google-cloud-aiplatform"),
        ("playwright", "playwright"), ("fpdf", "fpdf2"),
        ("multipart", "python-multipart"), ("PyQt6", "PyQt6"), 
        ("apscheduler", "apscheduler"), ("requests", "requests"),
        ("pydantic_settings", "pydantic-settings"),
        ("httpx", "httpx"), 
        ("google.protobuf", "protobuf") 
    ]
    missing = []
    for import_name, pip_name in required_libs:
        try:
            if importlib.util.find_spec(import_name) is None: missing.append(pip_name)
        except: 
            try:
                __import__(import_name)
            except ImportError:
                missing.append(pip_name)

    if missing:
        print("\n" + "!"*60)
        print("ERRORE CRITICO: Mancano librerie!")
        print(f'"{sys.executable}" -m pip install {" ".join(set(missing))}')
        print("!"*60 + "\n")
        sys.exit(1)
    print("All dependencies found.")

def collect_submodules(base_dir):
    modules = []
    if not os.path.exists(base_dir): return modules
    print(f"Auto-collecting modules from: {base_dir}...")
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                rel_path = os.path.relpath(os.path.join(root, file), ".")
                module_name = rel_path.replace(os.sep, ".")[:-3]
                modules.append(module_name)
    return modules

# --- FUNZIONE PRINCIPALE DI BUILD ---

def build():
    kill_existing_process()
    check_dependencies()

    if os.path.exists(DIST_DIR):
        try:
            shutil.rmtree(DIST_DIR)
        except PermissionError:
            print("\nERRORE: File bloccato. Chiudi Intelleo.exe.")
            sys.exit(1)
            
    os.makedirs(OBF_DIR, exist_ok=True)

    auto_detected_libs = scan_imports(["app", "desktop_app"])

    print("\n--- Step 1: Obfuscating with PyArmor ---")
    
    # Offusca le cartelle app, desktop_app E il file launcher.py
    cmd_pyarmor = [
        sys.executable, "-m", "pyarmor.cli", "gen",
        "-O", OBF_DIR,
        "-r", "app", "desktop_app", ENTRY_SCRIPT
    ]
    run_command(cmd_pyarmor)

    print("\n--- Step 2: Preparing Assets for Packaging ---")
    
    # Funzione helper per copiare cartelle
    def copy_dir_if_exists(src, dst_name):
        full_src = src
        full_dst = os.path.join(OBF_DIR, dst_name)
        if os.path.exists(full_src):
            if os.path.exists(full_dst): shutil.rmtree(full_dst)
            shutil.copytree(full_src, full_dst, dirs_exist_ok=True)
            print(f"Copied assets: {full_src} -> {full_dst}")

    copy_dir_if_exists("desktop_app/assets", "desktop_app/assets")
    copy_dir_if_exists("desktop_app/icons", "desktop_app/icons")

    # Copia file configurazione se esistono
    if os.path.exists("requirements.txt"):
        shutil.copy("requirements.txt", os.path.join(OBF_DIR, "requirements.txt"))
    if os.path.exists(".env"):
        shutil.copy(".env", os.path.join(OBF_DIR, ".env"))

    print("\n--- Step 3: Packaging with PyInstaller ---")
    
    sep = ";" if os.name == 'nt' else ":"
    runtime_dir = None
    
    # Cerca la cartella runtime generata da PyArmor
    for name in os.listdir(OBF_DIR):
        if name.startswith("pyarmor_runtime_") and os.path.isdir(os.path.join(OBF_DIR, name)):
            runtime_dir = name
            break
            
    if not runtime_dir:
        print("ERROR: PyArmor runtime folder not found inside obfuscated dir!")
        sys.exit(1)

    # Definizione dati da includere nell'EXE
    add_data = [
        f"desktop_app/assets{sep}desktop_app/assets",
        f"desktop_app/icons{sep}desktop_app/icons",
        f"{os.path.join(OBF_DIR, runtime_dir)}{sep}{runtime_dir}"
    ]

    cmd_pyinstaller = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onefile",
        "--windowed", # Nasconde la console (mettilo a --console se vuoi debuggare)
        "--clean",
        "--distpath", os.path.join(DIST_DIR, "package"),
        "--workpath", os.path.join(DIST_DIR, "build"),
        f"--paths={OBF_DIR}", # Importante: Cerca i moduli nella cartella offuscata
    ]
    
    for d in add_data:
        cmd_pyinstaller.extend(["--add-data", d])

    # --- FIX AGGRESSIVO PER GOOGLE CLOUD & PROTOBUF ---
    # Raccogliamo tutto ciò che riguarda google cloud e aiplatform
    cmd_pyinstaller.extend(["--collect-all", "google.cloud"])
    cmd_pyinstaller.extend(["--collect-all", "google.cloud.aiplatform"]) 
    cmd_pyinstaller.extend(["--collect-all", "google_cloud_aiplatform"]) 
    cmd_pyinstaller.extend(["--collect-all", "google.generativeai"])
    cmd_pyinstaller.extend(["--collect-all", "playwright"])
    cmd_pyinstaller.extend(["--collect-all", "grpc"])
    cmd_pyinstaller.extend(["--collect-all", "proto"])
    cmd_pyinstaller.extend(["--collect-all", "google.protobuf"]) 

    # LISTA IMPORT MANUALE CRITICI
    manual_hidden_imports = [
        "sqlalchemy.sql.default_comparator",
        "pysqlite2", "MySQLdb", "psycopg2", "dotenv",
        "fastapi", "starlette",
        "uvicorn.loops.auto", "uvicorn.protocols.http.auto", "uvicorn.lifespan.on",
        "multipart", "python_multipart",
        "PyQt6.QtSvg", "PyQt6.QtNetwork", "PyQt6.QtPrintSupport",
        "PyQt6.QtWidgets", "PyQt6.QtCore", "PyQt6.QtGui",
        
        # --- FIX EMAIL (AGGIUNTO email.mime.image) ---
        "email.mime.text", "email.mime.multipart", "email.mime.application",
        "email.mime.base", "email.mime.image", "email.header", "email.utils", "email.encoders",
        # ---------------------------------------------

        "pydantic_settings",
        "httpx", 
        
        # --- GOOGLE IMPORTS SPECIFICI ---
        "google.cloud.aiplatform",
        "google.cloud.aiplatform_v1",
        "google.cloud.aiplatform.gapic",
        "google.api_core",
        "google.auth",
        "google.protobuf", 
        "grpc",
        
        "pandas._libs.tslibs.base",
        "playwright.sync_api",
        "apscheduler.triggers.interval", "apscheduler.triggers.cron",
    ]

    # Unione di tutti gli import necessari
    all_hidden_imports = list(set(manual_hidden_imports + auto_detected_libs))
    all_hidden_imports.extend(collect_submodules("desktop_app"))
    all_hidden_imports.extend(collect_submodules("app"))

    for imp in all_hidden_imports:
        cmd_pyinstaller.extend(["--hidden-import", imp])

    # PUNTO DI INGRESSO: Il launcher.py offuscato
    cmd_pyinstaller.append(os.path.join(OBF_DIR, ENTRY_SCRIPT))

    run_command(cmd_pyinstaller)

    exe_path = os.path.join(DIST_DIR, 'package', f'{APP_NAME}.exe')
    print("\n" + "="*60)
    print(f"BUILD COMPLETATA!")
    print(f"Eseguibile: {exe_path}")
    print("="*60 + "\n")

if __name__ == "__main__":
    build()