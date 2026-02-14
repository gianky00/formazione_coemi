"""
Script di verifica ambiente di build per Nuitka.
Esegui prima di ogni build per evitare errori evitabili.
"""

import os
import subprocess
import sys
from pathlib import Path

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


def check_python_version():
    """Verifica versione Python >= 3.12"""
    print("🐍 Verifico versione Python...")
    version = sys.version_info
    if version.major == 3 and version.minor >= 12:
        print(f"   ✅ Python {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"   ❌ Python {version.major}.{version.minor}.{version.micro} (richiesto >= 3.12)")
        return False


def check_nuitka():
    """Verifica installazione Nuitka"""
    print("📦 Verifico Nuitka...")
    try:
        # Use python -m nuitka for Windows compatibility
        result = subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            # Parse version from first line (e.g., "2.8.9")
            output = result.stdout.strip()
            if output:
                version = output.split("\n")[0].strip()
                print(f"   ✅ Nuitka {version}")
                return True
    except FileNotFoundError:
        print("   ❌ Nuitka non trovato. Esegui: pip install nuitka")
    except subprocess.TimeoutExpired:
        print("   ❌ Timeout durante verifica Nuitka")
    except Exception as e:
        print(f"   ❌ Errore: {e}")
    return False


def check_msvc():
    """Verifica compilatore MSVC usando Nuitka discovery"""
    print("🔧 Verifico MSVC Compiler...")

    # Method 1: Check via Nuitka's own discovery (most reliable)
    try:
        result = subprocess.run(
            [sys.executable, "-m", "nuitka", "--version"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        if result.returncode == 0 and "Version C compiler:" in result.stdout:
            # Extract compiler info from Nuitka output
            for line in result.stdout.split("\n"):
                if "Version C compiler:" in line:
                    compiler_info = line.replace("Version C compiler:", "").strip()
                    print(f"   ✅ MSVC (via Nuitka): {compiler_info}")
                    return True
    except Exception:
        pass

    # Method 2: Direct cl.exe check (fallback)
    try:
        result = subprocess.run(["cl.exe"], capture_output=True, text=True, timeout=10)
        if "Microsoft (R) C/C++ Optimizing Compiler" in result.stderr:
            lines = result.stderr.split("\n")
            version_line = [line for line in lines if "Version" in line]
            if version_line:
                print(f"   ✅ {version_line[0].strip()}")
                return True
    except FileNotFoundError:
        pass
    except Exception:
        pass

    # Method 3: Check standard Visual Studio paths
    vs_paths = [
        r"C:\Program Files\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC",
        r"C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Tools\MSVC",
        r"C:\Program Files\Microsoft Visual Studio\2022\Professional\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\VC\Tools\MSVC",
        r"C:\Program Files (x86)\Microsoft Visual Studio\18\BuildTools\VC\Tools\MSVC",
    ]

    for vs_path in vs_paths:
        if os.path.exists(vs_path):
            # Find latest MSVC version
            try:
                versions = os.listdir(vs_path)
                if versions:
                    latest = sorted(versions)[-1]
                    cl_path = os.path.join(vs_path, latest, "bin", "Hostx64", "x64", "cl.exe")
                    if os.path.exists(cl_path):
                        print(f"   ✅ MSVC trovato: {cl_path}")
                        return True
            except Exception:
                continue

    print("   ❌ cl.exe non trovato. Installa Visual Studio Build Tools.")
    print(
        "      Download: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022"
    )
    return False


def check_frontend_build():
    """Verifica che guide_frontend sia buildato"""
    print("⚛️  Verifico build React (guide_frontend)...")

    # Determina root del progetto
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent  # admin/tools -> admin -> root

    dist_path = project_root / "guide_frontend" / "dist"
    index_path = dist_path / "index.html"

    if dist_path.exists() and index_path.exists():
        print("   ✅ guide_frontend/dist/index.html trovato")
        return True
    else:
        print("   ❌ guide_frontend non buildato. Esegui: cd guide_frontend && npm run build")
        return False


def check_dependencies():
    """Verifica dipendenze Python critiche"""
    print("📚 Verifico dipendenze Python...")
    critical = ["PyQt6", "fastapi", "sqlalchemy", "nuitka", "zstandard"]
    missing = []

    for pkg in critical:
        try:
            # Handle special package names
            import_name = pkg.lower().replace("-", "_")
            if pkg == "PyQt6":
                import_name = "PyQt6"
            __import__(import_name)
            print(f"   ✅ {pkg}")
        except ImportError:
            print(f"   ❌ {pkg} mancante")
            missing.append(pkg)

    return len(missing) == 0


def check_license_files():
    """Verifica presenza file licenza"""
    print("🔐 Verifico file licenza...")

    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent

    license_dir = project_root / "Licenza"
    required_files = ["config.dat", "pyarmor.rkey", "manifest.json"]

    if not license_dir.exists():
        print(f"   ❌ Cartella Licenza non trovata in {license_dir}")
        return False

    missing = []
    for f in required_files:
        if (license_dir / f).exists():
            print(f"   ✅ Licenza/{f}")
        else:
            print(f"   ❌ Licenza/{f} mancante")
            missing.append(f)

    return len(missing) == 0


def main():
    print("\n" + "=" * 60)
    print("🔍 VERIFICA AMBIENTE DI BUILD - Intelleo + Nuitka")
    print("=" * 60 + "\n")

    checks = [
        ("Python Version", check_python_version),
        ("Nuitka", check_nuitka),
        ("MSVC Compiler", check_msvc),
        ("Frontend Build", check_frontend_build),
        ("Python Dependencies", check_dependencies),
        ("License Files", check_license_files),
    ]

    results = []
    for name, check_func in checks:
        result = check_func()
        results.append((name, result))
        print()  # Riga vuota tra checks

    # Riepilogo
    print("=" * 60)
    print("📊 RIEPILOGO")
    print("=" * 60)

    all_pass = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status}: {name}")
        if not passed:
            all_pass = False

    print("=" * 60)

    if all_pass:
        print("✅ Ambiente pronto per build Nuitka!")
        return 0
    else:
        print("❌ Correggere gli errori sopra prima di procedere.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
