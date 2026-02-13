import os
import shutil
import subprocess
import sys


def build_guide():
    print("[*] Building Modern Guide Frontend...")

    guide_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "guide_frontend")

    if not os.path.exists(guide_dir):
        print(f"[!] Guide directory not found at {guide_dir}")
        return False

    # Check for npm
    npm_cmd = shutil.which("npm")
    if not npm_cmd:
        print("[!] npm not found. Please install Node.js to build the guide.")
        return False

    try:
        # npm install
        print("[*] Running npm install...")
        subprocess.run([npm_cmd, "install"], cwd=guide_dir, check=True, shell=(os.name == "nt"))

        # npm run build
        print("[*] Running npm run build...")
        subprocess.run(
            [npm_cmd, "run", "build"], cwd=guide_dir, check=True, shell=(os.name == "nt")
        )

        dist_dir = os.path.join(guide_dir, "dist")
        if os.path.exists(os.path.join(dist_dir, "index.html")):
            print(f"[+] Guide built successfully at {dist_dir}")
            return True
        else:
            print("[!] Build failed. index.html not found.")
            return False

    except subprocess.CalledProcessError as e:
        print(f"[!] Error during build process: {e}")
        return False
    except Exception as e:
        print(f"[!] Unexpected error: {e}")
        return False


if __name__ == "__main__":
    success = build_guide()
    sys.exit(0 if success else 1)
