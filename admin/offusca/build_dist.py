import subprocess
import os
import shutil
import sys
import time
import importlib.util
import ast
import logging
import platform

# --- CONFIGURAZIONE ---
# 1. FIX PORTABILITÀ: Directory corrente = cartella dello script
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Calcola la ROOT del progetto (due livelli sopra scripts/tools)
# Esempio: formazione_coemi/admin/tools -> formazione_coemi
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

ENTRY_SCRIPT = "boot_loader.py"
APP_NAME = "Intelleo"
DIST_DIR = "dist"
OBF_DIR = os.path.join(DIST_DIR, "obfuscated")
BUILD_LOG = "build_log.txt"

# Setup Logging
file_handler = logging.FileHandler(BUILD_LOG, mode='w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# --- UTILITÀ DI SISTEMA ---

def log_and_print(message, level="INFO"):
    """Logga su file e stampa a video."""
    print(message)
    sys.stdout.flush()
    if level == "INFO":
        logger.info(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)

def run_command(cmd, cwd=None):
    """Esegue un comando shell stampandolo a video in tempo reale."""
    log_and_print(f"Running: {' '.join(cmd)}")

    process = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1,
        universal_newlines=True
    )

    while True:
        line = process.stdout.readline()
        if not line and process.poll() is not None:
            break
        if line:
            line = line.rstrip()
            print(line)
            sys.stdout.flush()
            logger.info(f"[CMD] {line}")

    return_code = process.poll()
    if return_code != 0:
        log_and_print(f"Error running command: {cmd}", "ERROR")
        sys.exit(return_code)

def kill_existing_process():
    """Uccide eventuali processi 'Intelleo.exe' rimasti appesi."""
    log_and_print("--- Step 0/7: Cleaning active processes ---")
    if os.name == 'nt':
        try:
            subprocess.run(["taskkill", "/F", "/IM", f"{APP_NAME}.exe"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log_and_print(f"Killed active {APP_NAME}.exe instances (if any).")
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
    log_and_print("--- Scanning source code for imports ---")
    detected_imports = set()
    std_libs = get_std_libs()

    # Also scan launcher.py explicitly as it's no longer the entry point but is imported
    files_to_scan = [os.path.join(ROOT_DIR, ENTRY_SCRIPT), os.path.join(ROOT_DIR, "launcher.py")]
    
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

    detected_imports.discard("app")
    detected_imports.discard("desktop_app")
    log_and_print(f"Auto-detected external libraries: {', '.join(sorted(detected_imports))}")
    return list(detected_imports)

def verify_environment():
    """Verifica lo stato dell'ambiente di build."""
    log_and_print("--- Step 1/7: Environment Diagnostics ---")
    log_and_print(f"Running with Python: {sys.executable}")

    # Verify PyInstaller availability
    try:
        import PyInstaller
        log_and_print(f"PyInstaller verified at: {os.path.dirname(PyInstaller.__file__)}")
    except ImportError:
        log_and_print("CRITICAL: PyInstaller module not found in this environment!", "ERROR")
        log_and_print("Please run: pip install pyinstaller", "ERROR")
        sys.exit(1)

    req_path = os.path.join(ROOT_DIR, "requirements.txt")
    if os.path.exists(req_path):
        log_and_print(f"Checking dependencies from {req_path}...")
        missing_packages = []
        with open(req_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                pkg_name = line.split('==')[0].split('>=')[0].split('[')[0]
                if importlib.util.find_spec(pkg_name) is None:
                    mapping = {
                        "python-dotenv": "dotenv",
                        "python-multipart": "multipart",
                        "PyQt6": "PyQt6",
                        "PyQt6-WebEngine": "PyQt6.QtWebEngineWidgets",
                        "google-generativeai": "google.generativeai",
                        "fpdf2": "fpdf",
                        "pydantic-settings": "pydantic_settings"
                    }
                    check_name = mapping.get(pkg_name, pkg_name)
                    found = False
                    try:
                        if importlib.util.find_spec(check_name) is not None: found = True
                    except: pass
                    if not found:
                        try:
                            __import__(check_name)
                            found = True
                        except ImportError:
                            pass
                    if not found:
                        missing_packages.append(pkg_name)

        if missing_packages:
            log_and_print(f"WARNING: Potential missing packages: {missing_packages}", "WARNING")
    else:
        log_and_print("requirements.txt not found!", "WARNING")

    iscc_path = shutil.which("ISCC.exe")
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]

    if not iscc_path and os.name == 'nt':
        for p in possible_paths:
            if os.path.exists(p):
                iscc_path = p
                break

    if iscc_path:
        log_and_print(f"Inno Setup Compiler found: {iscc_path}")
    else:
        log_and_print("CRITICAL: Inno Setup Compiler (ISCC.exe) not found!", "ERROR")
        if os.name == 'nt':
            log_and_print("Please install Inno Setup 6.", "ERROR")
            sys.exit(1)

    # Updated DLL list to include missing dependencies commonly causing Qt errors
    dlls_to_check = ["vcruntime140.dll", "msvcp140.dll", "msvcp140_1.dll", "concrt140.dll", "vccorlib140.dll"]
    system_dlls_found = {}
    if os.name == 'nt':
        sys32 = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32")
        for dll in dlls_to_check:
            path = os.path.join(sys32, dll)
            if os.path.exists(path):
                system_dlls_found[dll] = path
                log_and_print(f"System DLL found: {dll}")
            else:
                log_and_print(f"System DLL missing: {dll}", "WARNING")

    return iscc_path, system_dlls_found

def collect_submodules(base_dir):
    """Colleziona tutti i sottomoduli Python in una cartella."""
    modules = []
    full_path = os.path.join(ROOT_DIR, base_dir)
    if not os.path.exists(full_path): return modules
    log_and_print(f"Auto-collecting modules from: {full_path}...")
    for root, _, files in os.walk(full_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                rel_path = os.path.relpath(os.path.join(root, file), ROOT_DIR)
                module_name = rel_path.replace(os.sep, ".")[:-3]
                modules.append(module_name)
    return modules

def build():
    try:
        log_and_print("Starting Build Process...")

        log_and_print("\n--- Step 0/7: Generating Installer Assets ---")
        try:
            assets_script = os.path.join(ROOT_DIR, "tools", "prepare_installer_assets.py")
            if os.path.exists(assets_script):
                run_command([sys.executable, assets_script])
            else:
                log_and_print(f"WARNING: Assets script not found at {assets_script}", "WARNING")
        except Exception as e:
            log_and_print(f"Asset generation warning: {e}", "WARNING")

        kill_existing_process()

        iscc_exe, system_dlls = verify_environment()

        if os.path.exists(DIST_DIR):
            try:
                shutil.rmtree(DIST_DIR)
            except PermissionError:
                log_and_print("ERROR: File locked. Close Intelleo.exe or the dist folder.", "ERROR")
                sys.exit(1)

        os.makedirs(OBF_DIR, exist_ok=True)

        log_and_print("\n--- Step 2/7: Building Modern Guide Frontend ---")
        try:
            guide_build_script = os.path.join(ROOT_DIR, "tools", "build_guide.py")
            run_command([sys.executable, guide_build_script])
        except Exception as e:
            log_and_print(f"Guide build warning: {e}", "WARNING")

        auto_detected_libs = scan_imports(["app", "desktop_app"])

        log_and_print("\n--- Step 3/7: Obfuscating with PyArmor ---")
        # We obfuscate ENTRY_SCRIPT (boot_loader) and launcher.py
        cmd_pyarmor = [
            sys.executable, "-m", "pyarmor.cli", "gen",
            "-O", OBF_DIR,
            "-r", os.path.join(ROOT_DIR, "app"), os.path.join(ROOT_DIR, "desktop_app"),
            os.path.join(ROOT_DIR, ENTRY_SCRIPT), os.path.join(ROOT_DIR, "launcher.py")
        ]
        run_command(cmd_pyarmor)

        log_and_print("\n--- Step 4/7: Preparing Assets for Packaging ---")
        def copy_dir_if_exists(src, dst_name):
            full_src = os.path.join(ROOT_DIR, src)
            full_dst = os.path.join(OBF_DIR, dst_name)
            if os.path.exists(full_src):
                if os.path.exists(full_dst): shutil.rmtree(full_dst)
                shutil.copytree(full_src, full_dst, dirs_exist_ok=True)
                log_and_print(f"Copied assets: {full_src} -> {full_dst}")

        copy_dir_if_exists("desktop_app/assets", "desktop_app/assets")
        copy_dir_if_exists("desktop_app/icons", "desktop_app/icons")

        # COPY RUNTIME HOOK (CERCA NELLA CARTELLA CORRENTE)
        rthook_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rthook_pyqt6.py")
        rthook_dst = os.path.join(OBF_DIR, "rthook_pyqt6.py")
        if os.path.exists(rthook_src):
            shutil.copy(rthook_src, rthook_dst)
            log_and_print(f"Copied runtime hook: {rthook_src} -> {rthook_dst}")
        else:
            log_and_print(f"WARNING: rthook_pyqt6.py not found in {os.path.dirname(rthook_src)}", "WARNING")

        if os.path.exists(os.path.join(ROOT_DIR, "requirements.txt")):
            shutil.copy(os.path.join(ROOT_DIR, "requirements.txt"), os.path.join(OBF_DIR, "requirements.txt"))

        log_and_print("\n--- Step 5/7: Packaging with PyInstaller (This may take a while) ---")
        sep = ";" if os.name == 'nt' else ":"
        runtime_dir = None
        for name in os.listdir(OBF_DIR):
            if name.startswith("pyarmor_runtime_") and os.path.isdir(os.path.join(OBF_DIR, name)):
                runtime_dir = name
                break
        if not runtime_dir:
            log_and_print("ERROR: PyArmor runtime folder not found inside obfuscated dir!", "ERROR")
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
            "--console",
            "--clean",
            "--noconfirm",
            "--icon", os.path.join(OBF_DIR, "desktop_app", "icons", "icon.ico"),
            "--distpath", DIST_DIR,
            "--workpath", os.path.join(DIST_DIR, "build"),
            f"--paths={OBF_DIR}",
            f"--runtime-hook={os.path.join(OBF_DIR, 'rthook_pyqt6.py')}", 
        ]

        for d in add_data:
            cmd_pyinstaller.extend(["--add-data", d])

        # Explicitly collect packages
        cmd_pyinstaller.extend(["--collect-all", "google.cloud"])
        cmd_pyinstaller.extend(["--collect-all", "google.cloud.aiplatform"])
        cmd_pyinstaller.extend(["--collect-all", "google.generativeai"])
        cmd_pyinstaller.extend(["--collect-all", "grpc"])
        cmd_pyinstaller.extend(["--collect-all", "google.protobuf"])
        cmd_pyinstaller.extend(["--collect-all", "desktop_app"])

        # FIX: Collect specific WebEngine modules to prevent "ModuleNotFoundError"
        cmd_pyinstaller.extend(["--collect-all", "PyQt6.QtWebEngineWidgets"])
        cmd_pyinstaller.extend(["--collect-all", "PyQt6.QtWebEngineCore"])
        cmd_pyinstaller.extend(["--collect-all", "PyQt6.QtWebChannel"])
        cmd_pyinstaller.extend(["--collect-all", "PyQt6-WebEngine"])

        # New: Collect Auth libraries explicitly
        cmd_pyinstaller.extend(["--collect-all", "passlib"])
        cmd_pyinstaller.extend(["--collect-all", "bcrypt"])
        cmd_pyinstaller.extend(["--collect-all", "jose"])
        cmd_pyinstaller.extend(["--collect-all", "cryptography"])

        # New: Collect PyQt6 base to ensure plugins are found
        cmd_pyinstaller.extend(["--collect-all", "PyQt6"])

        # Collect missing dependencies
        cmd_pyinstaller.extend(["--collect-all", "geoip2"])
        cmd_pyinstaller.extend(["--collect-all", "user_agents"])
        cmd_pyinstaller.extend(["--collect-all", "apscheduler"])

        manual_hidden_imports = [
            "launcher", 
            "views", "utils", "components", "api_client",
            "main_window_ui", "edit_dialog", "gantt_item", "view_models",
            "desktop_app.main", 
            "desktop_app.components", 
            "desktop_app.views", "desktop_app.utils", "desktop_app.components",
            "sqlalchemy.sql.default_comparator", "sqlalchemy.dialects.sqlite",
            "pysqlite2", "MySQLdb", "psycopg2", "dotenv",
            "fastapi", "starlette",
            "uvicorn.logging", "uvicorn.loops", "uvicorn.loops.auto",
            "uvicorn.protocols", "uvicorn.protocols.http", "uvicorn.protocols.http.auto",
            "uvicorn.lifespan.on", "multipart", "python_multipart",
            "PyQt6.QtSvg", "PyQt6.QtNetwork", "PyQt6.QtPrintSupport",
            "PyQt6.QtWidgets", "PyQt6.QtCore", "PyQt6.QtGui",
            # FIX: Hidden imports vitali per prevenire il crash iniziale
            "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebEngineCore", "PyQt6.QtWebChannel",
            "email.mime.text", "email.mime.multipart", "email.mime.application",
            "email.mime.base", "email.mime.image", "email.header", "email.utils",
            "email.encoders", "encodings",
            "pydantic_settings", "httpx",
            "google.cloud.aiplatform", "google.cloud.aiplatform_v1",
            "google.api_core", "google.auth", "google.protobuf", "grpc",
            "passlib", "passlib.handlers.bcrypt",
            "bcrypt",
            "jose", "jose.backends.cryptography_backend",
            "cryptography", "cryptography.hazmat.backends.openssl",
            "pandas", "tenacity", "fpdf", "ua_parser"
        ]

        all_hidden_imports = list(set(manual_hidden_imports + auto_detected_libs))
        all_hidden_imports.extend(collect_submodules("desktop_app"))
        all_hidden_imports.extend(collect_submodules("app"))

        for imp in all_hidden_imports:
            cmd_pyinstaller.extend(["--hidden-import", imp])

        # Point to the obfuscated boot_loader
        cmd_pyinstaller.append(os.path.join(OBF_DIR, ENTRY_SCRIPT))

        run_command(cmd_pyinstaller)

        log_and_print("\n--- Step 6/7: Post-Build Cleanup & DLL Injection ---")

        # FIX: Uso percorso assoluto per output folder
        output_folder = os.path.abspath(os.path.join(DIST_DIR, APP_NAME))

        if os.name == 'nt':
            dll_dest_dir = os.path.join(output_folder, "dll")
            os.makedirs(dll_dest_dir, exist_ok=True)
            for dll_name, dll_path in system_dlls.items():
                dest = os.path.join(dll_dest_dir, dll_name)
                if not os.path.exists(dest):
                    shutil.copy(dll_path, dest)
                    log_and_print(f"Injected {dll_name} into build/dll folder.")

        # --- GESTIONE LICENZA (UPDATE RICHIESTO) ---
        # "il file pyarmor.rkey lo trovi in formazione_coemi\Licenza tu devi importare la cartella formazione_coemi\Licenza"
        
        lic_dest_dir = os.path.join(output_folder, "Licenza")
        # Rimuoviamo la cartella di destinazione se esiste per partire puliti
        if os.path.exists(lic_dest_dir):
            shutil.rmtree(lic_dest_dir)
        
        # Percorso sorgente: formazione_coemi/Licenza
        lic_src_dir = os.path.join(ROOT_DIR, "Licenza")
        
        if os.path.exists(lic_src_dir):
            log_and_print(f"Importing License folder from: {lic_src_dir}")
            shutil.copytree(lic_src_dir, lic_dest_dir)
            log_and_print("License folder successfully imported.")
        else:
            log_and_print(f"CRITICAL WARNING: License folder not found at {lic_src_dir}", "WARNING")
            # Fallback: crea la cartella vuota per evitare errori nel setup
            os.makedirs(lic_dest_dir, exist_ok=True)


        log_and_print("\n--- Step 7/7: Compiling Installer with Inno Setup ---")

        # FIX: Percorso relativo allo script per trovare il setup.iss
        iss_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "crea_setup", "setup_script.iss"))
        
        # Fallback se non trovato nel percorso standard
        if not os.path.exists(iss_path):
             iss_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "setup_script.iss"))

        if not os.path.exists(iss_path):
            log_and_print(f"Setup script not found at: {iss_path}", "ERROR")
            sys.exit(1)

        # FIX: Passiamo il path assoluto di output_folder a Inno Setup
        cmd_iscc = [
            iscc_exe,
            f"/DMyAppVersion=1.0.0",
            f"/DBuildDir={output_folder}",
            iss_path
        ]

        run_command(cmd_iscc)

        log_and_print("="*60)
        log_and_print("BUILD AND PACKAGING COMPLETE SUCCESS!")
        log_and_print("="*60)

    except Exception as e:
        logger.exception("FATAL ERROR DURING BUILD:")
        sys.exit(1)

if __name__ == "__main__":
    build()