
import subprocess
import os
import shutil
import sys
import logging
from desktop_app.constants import FILE_REQUIREMENTS

# --- CONFIGURAZIONE ---
os.chdir(os.path.dirname(os.path.abspath(__file__)))
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

ENTRY_SCRIPT = "boot_loader.py"
APP_NAME = "Intelleo"
DIST_DIR = "dist"
BUILD_LOG = "build_nuitka_log.txt"

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

def build_nuitka():
    try:
        # 0. Pre-check for Nuitka
        try:
            import nuitka
        except ImportError:
            log_and_print("CRITICAL: Nuitka not found! Please run 'pip install nuitka' or 'pip install -r requirements.txt'.", "ERROR")
            sys.exit(1)

        log_and_print("Starting Nuitka Build Process...")

        # 1. Clean previous build
        if os.path.exists(DIST_DIR):
            shutil.rmtree(DIST_DIR)
        os.makedirs(DIST_DIR, exist_ok=True)

        # 2. Prepare Assets
        assets_script = os.path.join(ROOT_DIR, "tools", "prepare_installer_assets.py")
        if os.path.exists(assets_script):
            run_command([sys.executable, assets_script])

        # 3. Build Guide
        guide_build_script = os.path.join(ROOT_DIR, "tools", "build_guide.py")
        if os.path.exists(guide_build_script):
            run_command([sys.executable, guide_build_script])

        # 4. Run Nuitka
        # Determine output directory
        output_dir = os.path.join(DIST_DIR, f"{APP_NAME}.dist")

        cmd = [
            sys.executable, "-m", "nuitka",
            "--standalone",
            "--enable-plugin=pyqt6",
            "--include-data-dir=desktop_app/assets=desktop_app/assets",
            "--include-data-dir=desktop_app/icons=desktop_app/icons",
            "--include-data-dir=guide_frontend/dist=guide/dist",
            "--include-data-dir=docs=docs", # Include docs folder (LYRA_PROFILE.md)
            "--output-dir=" + DIST_DIR,
            "--file-reference-choice=runtime", # Needed for __file__ compatibility
            "--company-name=Intelleo Security",
            "--product-name=Intelleo",
            "--file-version=1.0.0",
            "--product-version=1.0.0",
            "--windows-console-mode=disable", # Hide console
            "--nofollow-import-to=pytest", # Exclude test libs
            "--nofollow-import-to=unittest",
            os.path.join(ROOT_DIR, ENTRY_SCRIPT)
        ]

        # Windows Icon
        icon_path = os.path.join(ROOT_DIR, "desktop_app", "icons", "icon.ico")
        if os.path.exists(icon_path):
            cmd.append(f"--windows-icon-from-ico={icon_path}")

        run_command(cmd, cwd=ROOT_DIR)

        # 5. Post-Build: Rename output folder to match App Name expected by Inno Setup
        final_output = os.path.join(DIST_DIR, APP_NAME)
        if os.path.exists(output_dir):
            if os.path.exists(final_output): shutil.rmtree(final_output)
            os.rename(output_dir, final_output)
            log_and_print(f"Renamed {output_dir} to {final_output}")
        else:
            # Maybe Nuitka named it boot_loader.dist?
            default_dist = os.path.join(DIST_DIR, "boot_loader.dist")
            if os.path.exists(default_dist):
                os.rename(default_dist, final_output)
                log_and_print(f"Renamed {default_dist} to {final_output}")

        # 6. Copy License Folder (Initial Seed)
        lic_src = os.path.join(ROOT_DIR, "Licenza")
        lic_dst = os.path.join(final_output, "Licenza")
        if os.path.exists(lic_src):
            shutil.copytree(lic_src, lic_dst, dirs_exist_ok=True)

        # 7. Compile Installer
        iscc_exe = shutil.which("ISCC.exe")
        if not iscc_exe and os.name == 'nt':
             possible_paths = [
                r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
                r"C:\Program Files\Inno Setup 6\ISCC.exe",
            ]
             for p in possible_paths:
                if os.path.exists(p):
                    iscc_exe = p
                    break

        if iscc_exe:
            iss_path = os.path.join(ROOT_DIR, "admin", "crea_setup", "setup_script.iss")
            cmd_iscc = [
                 iscc_exe,
                 f"/dBuildDir={final_output}",
                 "/dMyAppVersion=1.0.0",
                 iss_path
             ]
            run_command(cmd_iscc)
        else:
            log_and_print("ISCC not found, skipping installer compilation.")

        log_and_print("NUITKA BUILD COMPLETE SUCCESS!")

    except Exception:
        logger.exception("FATAL ERROR DURING BUILD:")
        sys.exit(1)

if __name__ == "__main__":
    build_nuitka()
