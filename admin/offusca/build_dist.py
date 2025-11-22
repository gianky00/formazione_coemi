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
# Forza la directory di lavoro alla cartella dove si trova questo script.
os.chdir(os.path.dirname(os.path.abspath(__file__)))

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
ENTRY_SCRIPT = "launcher.py"
APP_NAME = "Intelleo"
DIST_DIR = "dist"
OBF_DIR = os.path.join(DIST_DIR, "obfuscated")
BUILD_LOG = "build_log.txt"

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(BUILD_LOG, mode='w', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger()

# --- UTILITÀ DI SISTEMA ---

def run_command(cmd, cwd=None):
    """Esegue un comando shell stampandolo a video."""
    logger.info(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
    if result.returncode != 0:
        logger.error(f"Error running command: {cmd}")
        logger.error(f"STDOUT: {result.stdout}")
        logger.error(f"STDERR: {result.stderr}")
        sys.exit(result.returncode)
    return result.stdout

def kill_existing_process():
    """Uccide eventuali processi 'Intelleo.exe' rimasti appesi."""
    logger.info("--- Step 0: Cleaning active processes ---")
    if os.name == 'nt':
        try:
            subprocess.run(["taskkill", "/F", "/IM", f"{APP_NAME}.exe"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            logger.info(f"Killed active {APP_NAME}.exe instances (if any).")
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
    logger.info("--- Scanning source code for imports ---")
    detected_imports = set()
    std_libs = get_std_libs()

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

    detected_imports.discard("app")
    detected_imports.discard("desktop_app")
    logger.info(f"Auto-detected external libraries: {', '.join(sorted(detected_imports))}")
    return list(detected_imports)

def verify_environment():
    """Verifica lo stato dell'ambiente di build."""
    logger.info("--- Environment Diagnostics ---")

    # 1. Verifica Requirements
    req_path = os.path.join(ROOT_DIR, "requirements.txt")
    if os.path.exists(req_path):
        logger.info(f"Checking dependencies from {req_path}...")
        # Parsing semplice requirements.txt per controllare se i pacchetti sono installati
        # Nota: Questo è un controllo di base. Pip check potrebbe essere più accurato ma lento.
        missing_packages = []
        with open(req_path, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'): continue
                pkg_name = line.split('==')[0].split('>=')[0].split('[')[0]
                if importlib.util.find_spec(pkg_name) is None:
                    # Tentativo di mapping nome pip -> nome import (gestione casi comuni)
                    mapping = {
                        "python-dotenv": "dotenv",
                        "python-multipart": "multipart",
                        "PyQt6": "PyQt6",
                        "PyQt6-WebEngine": "PyQt6.QtWebEngineWidgets", # Approximation
                        "google-generativeai": "google.generativeai",
                        "fpdf2": "fpdf",
                        "pydantic-settings": "pydantic_settings"
                    }
                    check_name = mapping.get(pkg_name, pkg_name)

                    # Check alternativo
                    found = False
                    try:
                        if importlib.util.find_spec(check_name) is not None: found = True
                    except: pass

                    if not found:
                         # Ultimo tentativo: __import__
                        try:
                            __import__(check_name)
                            found = True
                        except ImportError:
                            pass

                    if not found:
                        missing_packages.append(pkg_name)

        if missing_packages:
            logger.warning(f"Potential missing packages (or import name mismatch): {missing_packages}")
            # Non blocchiamo qui drasticamente perché il mapping pip->import è fallace,
            # ma avvisiamo l'utente.
    else:
        logger.warning("requirements.txt not found!")

    # 2. Cerca ISCC (Inno Setup Compiler)
    iscc_path = None
    possible_paths = [
        r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
        r"C:\Program Files\Inno Setup 6\ISCC.exe",
    ]

    # Check PATH first
    iscc_path = shutil.which("ISCC.exe")

    if not iscc_path and os.name == 'nt':
        for p in possible_paths:
            if os.path.exists(p):
                iscc_path = p
                break

    if iscc_path:
        logger.info(f"Inno Setup Compiler found: {iscc_path}")
    else:
        logger.error("CRITICAL: Inno Setup Compiler (ISCC.exe) not found! Installer generation will fail.")
        if os.name == 'nt':
            logger.error("Please install Inno Setup 6.")
            sys.exit(1)

    # 3. Cerca DLL critiche (Windows Only)
    dlls_to_check = ["vcruntime140.dll", "msvcp140.dll"]
    system_dlls_found = {}

    if os.name == 'nt':
        sys32 = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32")
        for dll in dlls_to_check:
            path = os.path.join(sys32, dll)
            if os.path.exists(path):
                system_dlls_found[dll] = path
                logger.info(f"System DLL found: {dll} at {path}")
            else:
                logger.warning(f"System DLL missing: {dll}. It won't be injected automatically.")

    return iscc_path, system_dlls_found

def collect_submodules(base_dir):
    """Colleziona tutti i sottomoduli Python in una cartella."""
    modules = []
    full_path = os.path.join(ROOT_DIR, base_dir)
    if not os.path.exists(full_path): return modules
    logger.info(f"Auto-collecting modules from: {full_path}...")
    for root, _, files in os.walk(full_path):
        for file in files:
            if file.endswith(".py") and file != "__init__.py":
                rel_path = os.path.relpath(os.path.join(root, file), ROOT_DIR)
                module_name = rel_path.replace(os.sep, ".")[:-3]
                modules.append(module_name)
    return modules

# --- FUNZIONE PRINCIPALE DI BUILD ---

def build():
    try:
        logger.info("Starting Build Process...")
        kill_existing_process()

        # --- STEP 1: ENV CHECK ---
        iscc_exe, system_dlls = verify_environment()

        if os.path.exists(DIST_DIR):
            try:
                shutil.rmtree(DIST_DIR)
            except PermissionError:
                logger.error("ERROR: File locked. Close Intelleo.exe or the dist folder.")
                sys.exit(1)

        os.makedirs(OBF_DIR, exist_ok=True)

        # --- STEP 2: BUILD GUIDE FRONTEND ---
        logger.info("--- Step 2: Building Modern Guide Frontend ---")
        try:
            guide_build_script = os.path.join(ROOT_DIR, "tools", "build_guide.py")
            subprocess.run([sys.executable, guide_build_script], check=True)
        except Exception as e:
            logger.warning(f"Guide build failed: {e}. Proceeding...")

        auto_detected_libs = scan_imports(["app", "desktop_app"])

        # --- STEP 3: OBFUSCATION ---
        logger.info("--- Step 3: Obfuscating with PyArmor ---")

        cmd_pyarmor = [
            sys.executable, "-m", "pyarmor.cli", "gen",
            "-O", OBF_DIR,
            "-r", os.path.join(ROOT_DIR, "app"), os.path.join(ROOT_DIR, "desktop_app"), os.path.join(ROOT_DIR, ENTRY_SCRIPT)
        ]
        run_command(cmd_pyarmor)

        # --- STEP 4: ASSET PREP ---
        logger.info("--- Step 4: Preparing Assets for Packaging ---")

        def copy_dir_if_exists(src, dst_name):
            full_src = os.path.join(ROOT_DIR, src)
            full_dst = os.path.join(OBF_DIR, dst_name)
            if os.path.exists(full_src):
                if os.path.exists(full_dst): shutil.rmtree(full_dst)
                shutil.copytree(full_src, full_dst, dirs_exist_ok=True)
                logger.info(f"Copied assets: {full_src} -> {full_dst}")

        copy_dir_if_exists("desktop_app/assets", "desktop_app/assets")
        copy_dir_if_exists("desktop_app/icons", "desktop_app/icons")

        if os.path.exists(os.path.join(ROOT_DIR, "requirements.txt")):
            shutil.copy(os.path.join(ROOT_DIR, "requirements.txt"), os.path.join(OBF_DIR, "requirements.txt"))
        if os.path.exists(os.path.join(ROOT_DIR, ".env")):
            shutil.copy(os.path.join(ROOT_DIR, ".env"), os.path.join(OBF_DIR, ".env"))

        # --- STEP 5: PYINSTALLER ---
        logger.info("--- Step 5: Packaging with PyInstaller ---")

        sep = ";" if os.name == 'nt' else ":"
        runtime_dir = None

        for name in os.listdir(OBF_DIR):
            if name.startswith("pyarmor_runtime_") and os.path.isdir(os.path.join(OBF_DIR, name)):
                runtime_dir = name
                break

        if not runtime_dir:
            logger.error("ERROR: PyArmor runtime folder not found inside obfuscated dir!")
            sys.exit(1)

        add_data = [
            f"{os.path.join(OBF_DIR, 'desktop_app', 'assets')}{sep}desktop_app/assets",
            f"{os.path.join(OBF_DIR, 'desktop_app', 'icons')}{sep}desktop_app/icons",
            f"{os.path.join(OBF_DIR, runtime_dir)}{sep}{runtime_dir}",
            f"{os.path.join(ROOT_DIR, 'guide_frontend', 'dist')}{sep}guide"
        ]

        # Configurazione PyInstaller Robustissima
        cmd_pyinstaller = [
            sys.executable, "-m", "PyInstaller",
            "--name", APP_NAME,
            "--onedir",
            "--windowed",
            "--clean",
            "--noconfirm",
            "--icon", os.path.join(OBF_DIR, "desktop_app", "icons", "icon.ico"),
            "--distpath", DIST_DIR,
            "--workpath", os.path.join(DIST_DIR, "build"),
            f"--paths={OBF_DIR}",
        ]

        for d in add_data:
            cmd_pyinstaller.extend(["--add-data", d])

        cmd_pyinstaller.extend(["--collect-all", "google.cloud"])
        cmd_pyinstaller.extend(["--collect-all", "google.cloud.aiplatform"])
        cmd_pyinstaller.extend(["--collect-all", "google.generativeai"])
        cmd_pyinstaller.extend(["--collect-all", "grpc"])
        cmd_pyinstaller.extend(["--collect-all", "google.protobuf"])
        cmd_pyinstaller.extend(["--collect-all", "desktop_app"])

        # Espansione Hidden Imports
        manual_hidden_imports = [
            # Moduli Interni
            "views", "utils", "components", "api_client",
            "main_window_ui", "edit_dialog", "gantt_item", "view_models",
            "desktop_app.views", "desktop_app.utils", "desktop_app.components",

            # Database e Server
            "sqlalchemy.sql.default_comparator", "sqlalchemy.dialects.sqlite",
            "pysqlite2", "MySQLdb", "psycopg2", "dotenv",
            "fastapi", "starlette",
            "uvicorn.logging", "uvicorn.loops", "uvicorn.loops.auto",
            "uvicorn.protocols", "uvicorn.protocols.http", "uvicorn.protocols.http.auto",
            "uvicorn.lifespan.on", "multipart", "python_multipart",
            
            # PyQt6 Plugins & Core
            "PyQt6.QtSvg", "PyQt6.QtNetwork", "PyQt6.QtPrintSupport",
            "PyQt6.QtWidgets", "PyQt6.QtCore", "PyQt6.QtGui",
            "PyQt6.QtWebEngineWidgets", "PyQt6.QtWebEngineCore",

            # Email & Encoding
            "email.mime.text", "email.mime.multipart", "email.mime.application",
            "email.mime.base", "email.mime.image", "email.header", "email.utils",
            "email.encoders", "encodings",

            # Utilities
            "pydantic_settings", "httpx",

            # Google Specifici
            "google.cloud.aiplatform", "google.cloud.aiplatform_v1",
            "google.api_core", "google.auth", "google.protobuf", "grpc",
        ]

        all_hidden_imports = list(set(manual_hidden_imports + auto_detected_libs))
        all_hidden_imports.extend(collect_submodules("desktop_app"))
        all_hidden_imports.extend(collect_submodules("app"))

        for imp in all_hidden_imports:
            cmd_pyinstaller.extend(["--hidden-import", imp])

        cmd_pyinstaller.append(os.path.join(OBF_DIR, ENTRY_SCRIPT))

        run_command(cmd_pyinstaller)

        # --- STEP 6: DLL INJECTION & CLEANUP ---
        logger.info("--- Step 6: Post-Build Cleanup & DLL Injection ---")
        
        output_folder = os.path.join(DIST_DIR, APP_NAME)
        
        if os.name == 'nt':
            for dll_name, dll_path in system_dlls.items():
                dest = os.path.join(output_folder, dll_name)
                if not os.path.exists(dest):
                    shutil.copy(dll_path, dest)
                    logger.info(f"Injected {dll_name} into build folder.")
        
        # --- STEP 7: COMPILE INSTALLER ---
        logger.info("--- Step 7: Compiling Installer with Inno Setup ---")

        iss_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "crea_setup", "setup_script.iss"))

        if not os.path.exists(iss_path):
            logger.error(f"Setup script not found at: {iss_path}")
            sys.exit(1)

        # Costruzione comando ISCC con definizioni dinamiche
        cmd_iscc = [
            iscc_exe,
            f"/DMyAppVersion=1.0.0",  # TODO: Leggere versione da file
            f"/DBuildDir={output_folder}",
            iss_path
        ]

        run_command(cmd_iscc)

        logger.info("="*60)
        logger.info("BUILD AND PACKAGING COMPLETE SUCCESS!")
        logger.info("="*60)

    except Exception as e:
        logger.exception("FATAL ERROR DURING BUILD:")
        sys.exit(1)

if __name__ == "__main__":
    build()