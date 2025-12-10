import subprocess
import os
import shutil
import sys
import time
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
BUILD_LOG = "build_log.txt"

# Setup Logging
file_handler = logging.FileHandler(BUILD_LOG, mode='w', encoding='utf-8')
file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

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
    log_and_print("--- Step 0: Cleaning active processes ---")
    if os.name == 'nt':
        try:
            subprocess.run(["taskkill", "/F", "/IM", f"{APP_NAME}.exe"],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(1)
        except Exception:
            pass

def verify_environment():
    log_and_print("--- Step 1: Environment Diagnostics ---")
    log_and_print(f"Running with Python: {sys.executable}")

    # Check Nuitka
    try:
        import nuitka
        log_and_print(f"Nuitka verified: {nuitka.__version__}")
    except ImportError:
        log_and_print("CRITICAL: Nuitka module not found! Install with 'pip install nuitka'", "ERROR")
        sys.exit(1)

    # Check Inno Setup
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
        log_and_print("WARNING: Inno Setup Compiler (ISCC.exe) not found. Installer won't be built.", "WARNING")

    return iscc_path

def _build_guide():
    log_and_print("\n--- Step 2: Building Modern Guide Frontend ---")
    try:
        guide_build_script = os.path.join(ROOT_DIR, "tools", "build_guide.py")
        if os.path.exists(guide_build_script):
            run_command([sys.executable, guide_build_script])
        else:
            log_and_print("Guide build script not found, skipping.", "WARNING")
    except Exception as e:
        log_and_print(f"Guide build warning: {e}", "WARNING")

def _prepare_nuitka_cmd():
    """Prepares the Nuitka compilation command."""
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--plugin-enable=pyqt6",
        "--plugin-enable=pylint-warnings",
        "--remove-output",
        "--assume-yes-for-downloads",
        f"--output-dir={DIST_DIR}",
        f"--product-name={APP_NAME}",
        f"--file-description={APP_NAME} Security Application",
        "--copyright=Intelleo Copyright 2025",
        "--product-version=1.0.0",
        "--windows-icon-from-ico=desktop_app/icons/icon.ico",
        "--include-package=desktop_app",
        "--include-package=app",
        # Explicit hidden imports for critical libraries that might be missed
        "--include-package=sqlalchemy",
        "--include-package=passlib",
        "--include-package=bcrypt",
        "--include-package=jose",
        "--include-package=cryptography",
        "--include-package=geoip2",
        "--include-package=user_agents",
        "--include-package=apscheduler",
        "--include-package=sentry_sdk",
        "--include-package=fpdf",
        "--include-package=tenacity",
        "--include-package=pandas",
        "--include-package=win32com",
        "--include-package=win32api",
        "--include-package=pythoncom",
        "--include-package=engineio", # Often missed by socketio deps
        "--include-package=socketio",
        "--no-pyi-file", # Security: Don't expose interface files
    ]

    # Entry point
    cmd.append(os.path.join(ROOT_DIR, ENTRY_SCRIPT))

    return cmd

def _post_build_copy(output_dir):
    log_and_print("\n--- Step 4: Post-Build Asset Injection ---")

    # 1. Assets
    src_assets = os.path.join(ROOT_DIR, "desktop_app", "assets")
    dst_assets = os.path.join(output_dir, "desktop_app", "assets")
    if os.path.exists(src_assets):
        shutil.copytree(src_assets, dst_assets, dirs_exist_ok=True)
        log_and_print(f"Copied Assets: {dst_assets}")

    # 2. Icons
    src_icons = os.path.join(ROOT_DIR, "desktop_app", "icons")
    dst_icons = os.path.join(output_dir, "desktop_app", "icons")
    if os.path.exists(src_icons):
        shutil.copytree(src_icons, dst_icons, dirs_exist_ok=True)
        log_and_print(f"Copied Icons: {dst_icons}")

    # 3. Guide Frontend
    src_guide = os.path.join(ROOT_DIR, "guide_frontend", "dist")
    dst_guide = os.path.join(output_dir, "guide_frontend", "dist")
    if os.path.exists(src_guide):
        shutil.copytree(src_guide, dst_guide, dirs_exist_ok=True)
        log_and_print(f"Copied Guide: {dst_guide}")

    # 4. Docs
    src_docs = os.path.join(ROOT_DIR, "docs")
    dst_docs = os.path.join(output_dir, "docs")
    if os.path.exists(src_docs):
        shutil.copytree(src_docs, dst_docs, dirs_exist_ok=True)
        log_and_print(f"Copied Docs: {dst_docs}")

    # 5. Licenses (Config & Keys if present locally for testing)
    src_lic = os.path.join(ROOT_DIR, "Licenza")
    dst_lic = os.path.join(output_dir, "Licenza")
    if os.path.exists(src_lic):
        shutil.copytree(src_lic, dst_lic, dirs_exist_ok=True)
        log_and_print(f"Copied Licenses: {dst_lic}")

def build():
    try:
        log_and_print("Starting Nuitka Build Process...")

        kill_existing_process()
        iscc_exe = verify_environment()

        # Clean previous build
        if os.path.exists(DIST_DIR):
            try:
                shutil.rmtree(DIST_DIR)
            except PermissionError:
                log_and_print("ERROR: Dist folder locked.", "ERROR")
                sys.exit(1)
        os.makedirs(DIST_DIR, exist_ok=True)

        _build_guide()

        # Generate Nuitka Command
        log_and_print("\n--- Step 3: Compiling with Nuitka ---")
        cmd_nuitka = _prepare_nuitka_cmd()
        run_command(cmd_nuitka, cwd=ROOT_DIR)

        # Locate Output Directory
        # Nuitka with --standalone creates 'boot_loader.dist' (based on entry script name)
        output_folder_name = ENTRY_SCRIPT.replace(".py", ".dist")
        output_dir = os.path.join(ROOT_DIR, DIST_DIR, output_folder_name)
        
        if not os.path.exists(output_dir):
            log_and_print(f"CRITICAL: Build failed, output directory {output_dir} not found.", "ERROR")
            sys.exit(1)

        # Rename to 'Intelleo' for consistency
        final_output_dir = os.path.join(ROOT_DIR, DIST_DIR, APP_NAME)
        if os.path.exists(final_output_dir):
            shutil.rmtree(final_output_dir)
        os.rename(output_dir, final_output_dir)
        log_and_print(f"Build output moved to: {final_output_dir}")

        # Post-Build Steps
        _post_build_copy(final_output_dir)

        # Installer
        if iscc_exe:
             log_and_print("\n--- Step 5: Compiling Installer with Inno Setup ---")
             iss_path = os.path.abspath(os.path.join(ROOT_DIR, "admin", "crea_setup", "setup_script.iss"))

             cmd_iscc = [
                 iscc_exe,
                 f"/dBuildDir={final_output_dir}",
                 "/dMyAppVersion=1.0.0",
                 "setup_script.iss"
             ]
             run_command(cmd_iscc, cwd=os.path.dirname(iss_path))

        log_and_print("="*60)
        log_and_print("NUITKA BUILD COMPLETE SUCCESS!")
        log_and_print("="*60)

    except Exception:
        logger.exception("FATAL ERROR DURING BUILD:")
        sys.exit(1)

if __name__ == "__main__":
    build()
