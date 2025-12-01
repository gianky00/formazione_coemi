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
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

ENTRY_SCRIPT = "boot_loader.py"
APP_NAME = "Intelleo"
DIST_DIR = "dist"
OBF_DIR = os.path.join(DIST_DIR, "obfuscated")
# INSTALLER_ASSETS_DIR is no longer used for internal generation,
# but we keep the variable if needed for cleanup or compatibility
INSTALLER_ASSETS_DIR = os.path.join(DIST_DIR, "installer_assets")
BUILD_LOG = "build_log.txt"

# Setup Logging
file_handler = logging.FileHandler(BUILD_LOG, mode='w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# --- UTILITÀ DI SISTEMA ---

def log_and_print(message, level="INFO"):
    print(message)
    sys.stdout.flush()
    if level == "INFO":
        logger.info(message)
    elif level == "ERROR":
        logger.error(message)
    elif level == "WARNING":
        logger.warning(message)

def run_command(cmd, cwd=None):
    log_and_print(f"Running: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1, universal_newlines=True
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
    log_and_print("--- Step 0/7: Cleaning active processes ---")
    if os.name == 'nt':
        try:
            subprocess.run(["taskkill", "/F", "/IM", f"{APP_NAME}.exe"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
        except Exception:
            pass

def get_std_libs():
    libs = set(sys.builtin_module_names)
    try:
        libs.update(sys.stdlib_module_names)
    except AttributeError:
        pass
    return libs

def scan_imports(source_dirs):
    log_and_print("--- Scanning source code for imports ---")
    detected_imports = set()
    std_libs = get_std_libs()
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
    log_and_print("--- Step 1/7: Environment Diagnostics ---")
    log_and_print(f"Running with Python: {sys.executable}")

    # Check/Install Pillow for Asset Generation (Deprecated but kept if needed elsewhere)
    # The new asset generator uses PyQt6, so Pillow is less critical here,
    # but we verify PyInstaller which is critical.

    # Check PyInstaller
    try:
        import PyInstaller
        log_and_print(f"PyInstaller verified: {os.path.dirname(PyInstaller.__file__)}")
    except ImportError:
        log_and_print("CRITICAL: PyInstaller module not found!", "ERROR")
        sys.exit(1)

    req_path = os.path.join(ROOT_DIR, "requirements.txt")
    if os.path.exists(req_path):
        log_and_print(f"Checking dependencies from {req_path}...")

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
            sys.exit(1)

    # Check DLLs
    dlls_to_check = ["vcruntime140.dll", "msvcp140.dll", "msvcp140_1.dll", "concrt140.dll", "vccorlib140.dll"]
    system_dlls_found = {}
    if os.name == 'nt':
        sys32 = os.path.join(os.environ.get("SystemRoot", "C:\\Windows"), "System32")
        for dll in dlls_to_check:
            path = os.path.join(sys32, dll)
            if os.path.exists(path):
                system_dlls_found[dll] = path
    return iscc_path, system_dlls_found

def collect_submodules(base_dir):
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

        log_and_print("\n--- Step 0/7: Generating Installer Assets (Deep Space Theme) ---")

        assets_script = os.path.join(ROOT_DIR, "tools", "prepare_installer_assets.py")
        if os.path.exists(assets_script):
            cmd = [sys.executable, assets_script]
            # Use offscreen platform for headless environments
            if platform.system() == "Linux" or os.environ.get("HEADLESS_BUILD"):
                cmd.extend(["-platform", "offscreen"])
                # Also set env var to be safe
                os.environ["QT_QPA_PLATFORM"] = "offscreen"

            run_command(cmd)
        else:
            log_and_print(f"ERROR: Assets script not found at {assets_script}", "ERROR")
            sys.exit(1)

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

        rthook_src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rthook_pyqt6.py")
        rthook_dst = os.path.join(OBF_DIR, "rthook_pyqt6.py")
        if os.path.exists(rthook_src):
            shutil.copy(rthook_src, rthook_dst)

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
        cmd_pyinstaller.extend(["--collect-all", "PyQt6.QtWebEngineWidgets"])
        cmd_pyinstaller.extend(["--collect-all", "PyQt6.QtWebEngineCore"])
        cmd_pyinstaller.extend(["--collect-all", "PyQt6.QtWebChannel"])
        cmd_pyinstaller.extend(["--collect-all", "PyQt6-WebEngine"])
        cmd_pyinstaller.extend(["--collect-all", "passlib"])
        cmd_pyinstaller.extend(["--collect-all", "bcrypt"])
        cmd_pyinstaller.extend(["--collect-all", "jose"])
        cmd_pyinstaller.extend(["--collect-all", "cryptography"])
        cmd_pyinstaller.extend(["--collect-all", "PyQt6"])
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
            "win32com.client", "pythoncom", "win32api", "pywintypes", "win32timezone",
            "fastapi", "starlette",
            "uvicorn.logging", "uvicorn.loops", "uvicorn.loops.auto",
            "uvicorn.protocols", "uvicorn.protocols.http", "uvicorn.protocols.http.auto",
            "uvicorn.lifespan.on", "multipart", "python_multipart",
            "PyQt6.QtSvg", "PyQt6.QtNetwork", "PyQt6.QtPrintSupport",
            "PyQt6.QtWidgets", "PyQt6.QtCore", "PyQt6.QtGui",
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

        cmd_pyinstaller.append(os.path.join(OBF_DIR, ENTRY_SCRIPT))
        run_command(cmd_pyinstaller)

        log_and_print("\n--- Step 6/7: Post-Build Cleanup & DLL Injection ---")

        output_folder = os.path.abspath(os.path.join(DIST_DIR, APP_NAME))

        if os.name == 'nt':
            dll_dest_dir = os.path.join(output_folder, "dll")
            os.makedirs(dll_dest_dir, exist_ok=True)
            for dll_name, dll_path in system_dlls.items():
                dest = os.path.join(dll_dest_dir, dll_name)
                if not os.path.exists(dest):
                    shutil.copy(dll_path, dest)
                    log_and_print(f"Injected {dll_name} into build/dll folder.")

        lic_dest_dir = os.path.join(output_folder, "Licenza")
        if os.path.exists(lic_dest_dir):
            shutil.rmtree(lic_dest_dir)
        
        lic_src_dir = os.path.join(ROOT_DIR, "Licenza")
        
        if os.path.exists(lic_src_dir) and os.listdir(lic_src_dir):
            shutil.copytree(lic_src_dir, lic_dest_dir)
        else:
            os.makedirs(lic_dest_dir, exist_ok=True)


        log_and_print("\n--- Step 7/7: Compiling Installer with Inno Setup ---")
        
        # Use the MASTER ISS file in admin/crea_setup
        iss_path = os.path.abspath(os.path.join(ROOT_DIR, "admin", "crea_setup", "setup_script.iss"))

        # The BuildDir passed to Inno Setup must point to the PyInstaller output folder (output_folder)
        # We pass it as an absolute path for safety
        build_dir_abs = output_folder

        log_and_print(f"Using Master ISS: {iss_path}")
        log_and_print(f"Build Source Dir: {build_dir_abs}")

        if iscc_exe:
             log_and_print("Compiling with Inno Setup...")
             # Run ISCC from the directory where the ISS file lives, so relative paths in ISS (like OutputDir) work correctly
             iss_cwd = os.path.dirname(iss_path)

             cmd_iscc = [
                 iscc_exe,
                 f"/dBuildDir={build_dir_abs}",
                 f"/dMyAppVersion=1.0.0",
                 "setup_script.iss"
             ]

             run_command(cmd_iscc, cwd=iss_cwd)
        else:
             log_and_print("Skipping compilation (ISCC not found/Linux).")

        log_and_print("="*60)
        log_and_print("BUILD AND PACKAGING COMPLETE SUCCESS!")
        log_and_print("="*60)

    except Exception as e:
        logger.exception("FATAL ERROR DURING BUILD:")
        sys.exit(1)

if __name__ == "__main__":
    build()
