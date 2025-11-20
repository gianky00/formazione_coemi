import subprocess
import os
import shutil
import sys

def run_command(cmd, cwd=None):
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True)
    if result.returncode != 0:
        print(f"Error running command: {cmd}")
        sys.exit(result.returncode)

def build():
    # Configuration
    DIST_DIR = "dist"
    OBF_DIR = os.path.join(DIST_DIR, "obfuscated")

    # Clean previous build
    if os.path.exists(DIST_DIR):
        shutil.rmtree(DIST_DIR)
    os.makedirs(OBF_DIR, exist_ok=True)

    print("--- Step 1: Obfuscating with PyArmor ---")
    # Obfuscate 'app' and 'desktop_app'
    cmd_pyarmor = [
        "pyarmor", "gen",
        "-O", OBF_DIR,
        "-r", "app", "desktop_app"
    ]
    run_command(cmd_pyarmor)

    print("--- Step 2: Preparing for Packaging ---")
    # Copy launcher.py to obfuscated dir
    shutil.copy("launcher.py", os.path.join(OBF_DIR, "launcher.py"))

    # Restore desktop_app/main.py to plain text to handle license errors gracefully
    print("Restoring desktop_app/main.py to plain text...")
    shutil.copy("desktop_app/main.py", os.path.join(OBF_DIR, "desktop_app", "main.py"))

    # Copy assets
    def copy_dir_if_exists(src, dst):
        if os.path.exists(src):
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copytree(src, dst, dirs_exist_ok=True)
            print(f"Copied {src} -> {dst}")

    copy_dir_if_exists("desktop_app/assets", os.path.join(OBF_DIR, "desktop_app", "assets"))
    copy_dir_if_exists("desktop_app/icons", os.path.join(OBF_DIR, "desktop_app", "icons"))

    # Copy other necessary files
    if os.path.exists("requirements.txt"):
        shutil.copy("requirements.txt", os.path.join(OBF_DIR, "requirements.txt"))
    if os.path.exists(".env.example"):
        shutil.copy(".env.example", os.path.join(OBF_DIR, ".env.example"))

    print("--- Step 3: Packaging with PyInstaller ---")

    # Construct --add-data arguments. Separator is ; on Windows, : on Linux.
    sep = ";" if os.name == 'nt' else ":"

    # Assets paths relative to OBF_DIR (desktop_app/assets is inside OBF_DIR)
    # Source: desktop_app/assets (in OBF_DIR) -> Dest: desktop_app/assets
    add_data = [
        f"desktop_app/assets{sep}desktop_app/assets",
        f"desktop_app/icons{sep}desktop_app/icons"
    ]

    cmd_pyinstaller = [
        "pyinstaller",
        "--name", "Intelleo",
        "--onefile",
        "--windowed",
        "--clean",
        "--distpath", os.path.join(DIST_DIR, "package"),
        "--workpath", os.path.join(DIST_DIR, "build"),
        # Add data
        "--add-data", add_data[0],
        "--add-data", add_data[1],
        # Hidden imports commonly needed
        "--hidden-import", "sqlalchemy.sql.default_comparator",
        "--hidden-import", "uvicorn.loops.auto",
        "--hidden-import", "uvicorn.protocols.http.auto",
        "--hidden-import", "uvicorn.lifespan.on",
        "--hidden-import", "app.db.models", # Ensure models are found
        "--hidden-import", "app.api.routers.tuning",
        "--hidden-import", "app.api.routers.notifications",
        # Main script (launcher in OBF_DIR)
        os.path.join(OBF_DIR, "launcher.py")
    ]

    run_command(cmd_pyinstaller)

    print(f"Build complete. Executable in {os.path.join(DIST_DIR, 'package')}")

if __name__ == "__main__":
    build()
