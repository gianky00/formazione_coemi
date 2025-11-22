import subprocess
import os
import shutil
import sys
import time
import importlib.util
import ast

# --- FIX FONDAMENTALE PER CMD ---
# Forza la directory di lavoro alla cartella dove si trova questo script.
os.chdir(os.path.dirname(os.path.abspath(__file__)))
# --------------------------------

# --- CONFIGURAZIONE ---
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
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
    files_to_scan = [os.path.join(ROOT_DIR, ENTRY_SCRIPT)]
    
    for source_dir in source_dirs:
        full_source_dir = os.path.join(ROOT_DIR, source_dir)
        if not os.path.exists(full_source_dir): continue
        for root, _, files in os.walk(full_source_dir):
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
    """Verifica installazione librerie critiche."""
    print("--- Checking Build Dependencies ---")
    required_libs = [
        ("PyInstaller", "pyinstaller"), ("pyarmor", "pyarmor"),
        ("fastapi", "fastapi"), ("uvicorn", "uvicorn"), 
        ("sqlalchemy", "sqlalchemy"), 
        ("google.generativeai", "google-generativeai"),
        ("google.cloud.aiplatform", "google-cloud-aiplatform"),
        ("multipart", "python-multipart"), ("PyQt6", "PyQt6"), 
        ("requests", "requests"),
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
    """Colleziona tutti i sottomoduli Python in una cartella."""
    modules = []
    full_path = os.path.join(ROOT_DIR, base_dir)
    if not os.path.exists(full_path): return modules
    print(f"Auto-collecting modules from: {full_path}...")
    for root, _, files in os.walk(full_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                # Calcola il percorso relativo es: desktop_app\views\main.py -> desktop_app.views.main
                rel_path = os.path.relpath(os.path.join(root, file), ROOT_DIR)
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
            print("\nERRORE: File bloccato. Chiudi Intelleo.exe o la cartella dist.")
            sys.exit(1)
            
    os.makedirs(OBF_DIR, exist_ok=True)

    # --- STEP 0.5: BUILD GUIDE FRONTEND ---
    print("\n--- Step 0.5: Building Modern Guide Frontend ---")
    try:
        guide_build_script = os.path.join(ROOT_DIR, "tools", "build_guide.py")
        subprocess.run([sys.executable, guide_build_script], check=True)
    except Exception as e:
        print(f"WARNING: Guide build failed: {e}")
        print("Proceeding without updating guide...")

    auto_detected_libs = scan_imports(["app", "desktop_app"])

    print("\n--- Step 1: Obfuscating with PyArmor ---")
    
    cmd_pyarmor = [
        sys.executable, "-m", "pyarmor.cli", "gen",
        "-O", OBF_DIR,
        "-r", os.path.join(ROOT_DIR, "app"), os.path.join(ROOT_DIR, "desktop_app"), os.path.join(ROOT_DIR, ENTRY_SCRIPT)
    ]
    run_command(cmd_pyarmor)

    print("\n--- Step 2: Preparing Assets for Packaging ---")
    
    def copy_dir_if_exists(src, dst_name):
        full_src = os.path.join(ROOT_DIR, src)
        full_dst = os.path.join(OBF_DIR, dst_name)
        if os.path.exists(full_src):
            if os.path.exists(full_dst): shutil.rmtree(full_dst)
            shutil.copytree(full_src, full_dst, dirs_exist_ok=True)
            print(f"Copied assets: {full_src} -> {full_dst}")

    copy_dir_if_exists("desktop_app/assets", "desktop_app/assets")
    copy_dir_if_exists("desktop_app/icons", "desktop_app/icons")

    if os.path.exists(os.path.join(ROOT_DIR, "requirements.txt")):
        shutil.copy(os.path.join(ROOT_DIR, "requirements.txt"), os.path.join(OBF_DIR, "requirements.txt"))
    if os.path.exists(os.path.join(ROOT_DIR, ".env")):
        shutil.copy(os.path.join(ROOT_DIR, ".env"), os.path.join(OBF_DIR, ".env"))

    print("\n--- Step 3: Packaging with PyInstaller ---")
    
    sep = ";" if os.name == 'nt' else ":"
    runtime_dir = None
    
    for name in os.listdir(OBF_DIR):
        if name.startswith("pyarmor_runtime_") and os.path.isdir(os.path.join(OBF_DIR, name)):
            runtime_dir = name
            break
            
    if not runtime_dir:
        print("ERROR: PyArmor runtime folder not found inside obfuscated dir!")
        sys.exit(1)

    add_data = [
        f"{os.path.join(OBF_DIR, 'desktop_app', 'assets')}{sep}desktop_app/assets",
        f"{os.path.join(OBF_DIR, 'desktop_app', 'icons')}{sep}desktop_app/icons",
        f"{os.path.join(OBF_DIR, runtime_dir)}{sep}{runtime_dir}",
        f"{os.path.join(ROOT_DIR, 'guide_frontend', 'dist')}{sep}guide"
    ]

    cmd_pyinstaller = [
        sys.executable, "-m", "PyInstaller",
        "--name", APP_NAME,
        "--onedir",   
        "--windowed", # MODIFICATO: Niente console nera per l'utente finale
        "--clean",
        "--noconfirm",
        "--icon", os.path.join(OBF_DIR, "desktop_app", "icons", "icon.ico"),
        "--distpath", DIST_DIR, 
        "--workpath", os.path.join(DIST_DIR, "build"),
        f"--paths={OBF_DIR}",
    ]
    
    for d in add_data:
        cmd_pyinstaller.extend(["--add-data", d])

    # --- FIX AGGRESSIVO PER LE DIPENDENZE AI E INTERNALI ---
    # 1. Colleziona intere librerie complesse
    cmd_pyinstaller.extend(["--collect-all", "google.cloud"])
    cmd_pyinstaller.extend(["--collect-all", "google.cloud.aiplatform"]) 
    cmd_pyinstaller.extend(["--collect-all", "google.generativeai"])
    cmd_pyinstaller.extend(["--collect-all", "grpc"])
    cmd_pyinstaller.extend(["--collect-all", "google.protobuf"]) 
    cmd_pyinstaller.extend(["--collect-all", "desktop_app"]) # IMPORTANTE: Forza inclusione app

    # 2. Lista Import Manuale (Aggiunti i moduli mancanti dal log precedente)
    manual_hidden_imports = [
        # Moduli Interni che fallivano
        "views", "utils", "components", "api_client", 
        "main_window_ui", "edit_dialog", "gantt_item", "view_models",
        "desktop_app.views", "desktop_app.utils", "desktop_app.components",

        # Database e Server
        "sqlalchemy.sql.default_comparator",
        "pysqlite2", "MySQLdb", "psycopg2", "dotenv",
        "fastapi", "starlette",
        "uvicorn.loops.auto", "uvicorn.protocols.http.auto", "uvicorn.lifespan.on",
        "multipart", "python_multipart",
        
        # PyQt6 Plugins
        "PyQt6.QtSvg", "PyQt6.QtNetwork", "PyQt6.QtPrintSupport",
        "PyQt6.QtWidgets", "PyQt6.QtCore", "PyQt6.QtGui",
        "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebEngineCore",
        
        # Email
        "email.mime.text", "email.mime.multipart", "email.mime.application",
        "email.mime.base", "email.mime.image", "email.header", "email.utils", "email.encoders",

        # Utilities
        "pydantic_settings",
        "httpx", 
        
        # Google Specifici
        "google.cloud.aiplatform",
        "google.cloud.aiplatform_v1",
        "google.api_core",
        "google.auth",
        "google.protobuf", 
        "grpc",
    ]

    all_hidden_imports = list(set(manual_hidden_imports + auto_detected_libs))
    # Colleziona sottomoduli ma assicura che i path siano puliti
    all_hidden_imports.extend(collect_submodules("desktop_app"))
    all_hidden_imports.extend(collect_submodules("app"))

    for imp in all_hidden_imports:
        cmd_pyinstaller.extend(["--hidden-import", imp])

    cmd_pyinstaller.append(os.path.join(OBF_DIR, ENTRY_SCRIPT))

    run_command(cmd_pyinstaller)

    exe_path = os.path.join(DIST_DIR, APP_NAME, f'{APP_NAME}.exe')
    print("\n" + "="*60)
    print(f"BUILD COMPLETATA!")
    print(f"Cartella output: {os.path.join(DIST_DIR, APP_NAME)}")
    print(f"Eseguibile: {exe_path}")
    print("="*60 + "\n")

if __name__ == "__main__":
    build()