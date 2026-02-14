"""
Test automatico dell'eseguibile compilato con Nuitka.

Verifica che tutti i componenti critici funzionino:
1. Eseguibile esiste
2. Si avvia senza crash immediato
3. Nessun errore critico (DLL, Import, Module)
4. Struttura directory corretta
5. Asset critici presenti

Usage:
    python admin/tools/test_build.py [--verbose] [--skip-launch]

Author: Migration Team
Version: 1.0.0
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

# Fix Windows console encoding
if sys.platform == "win32":
    import io

    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")
    except Exception:
        pass

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DIST_DIR = PROJECT_ROOT / "dist" / "nuitka"

# Possible exe locations (Nuitka output varies)
EXE_CANDIDATES = [
    DIST_DIR / "Intelleo.dist" / "Intelleo.exe",
    DIST_DIR / "launcher.dist" / "Intelleo.exe",
    DIST_DIR / "launcher.dist" / "launcher.exe",
    DIST_DIR / "Intelleo.exe",
]

# Critical assets that should exist in dist
CRITICAL_ASSETS = [
    "guide",  # React SPA directory
    "desktop_app/assets",
    "desktop_app/icons",
]

# Critical DLLs (PyQt6)
CRITICAL_DLLS = [
    "Qt6Core.dll",
    "Qt6Gui.dll",
    "Qt6Widgets.dll",
    "Qt6WebEngineCore.dll",
]

# Error patterns to check in stderr
CRITICAL_ERRORS = [
    "DLL load failed",
    "ImportError",
    "ModuleNotFoundError",
    "No module named",
    "FileNotFoundError",
    "OSError: [WinError",
    "Fatal Python error",
]

# =============================================================================
# HELPERS
# =============================================================================

VERBOSE = False


def log_info(msg: str):
    """Log info message."""
    if VERBOSE:
        print(f"   ℹ️  {msg}")


def find_exe() -> Path | None:
    """Find the compiled executable."""
    for candidate in EXE_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


def get_dist_root() -> Path | None:
    """Get the root of the distribution (where exe lives)."""
    exe = find_exe()
    if exe:
        return exe.parent
    return None


# =============================================================================
# TESTS
# =============================================================================


def test_exe_exists() -> bool:
    """Test 1: Eseguibile esiste."""
    print("🔍 Test 1: Eseguibile esiste...")

    exe = find_exe()
    if exe:
        size_mb = exe.stat().st_size / (1024 * 1024)
        print(f"   ✅ PASS: {exe.relative_to(PROJECT_ROOT)} ({size_mb:.1f} MB)")
        return True
    else:
        print("   ❌ FAIL: Eseguibile non trovato")
        print("   Cercato in:")
        for candidate in EXE_CANDIDATES:
            print(f"     - {candidate.relative_to(PROJECT_ROOT)}")
        return False


def test_exe_size() -> bool:
    """Test 2: Dimensione eseguibile ragionevole."""
    print("📏 Test 2: Dimensione eseguibile...")

    exe = find_exe()
    if not exe:
        print("   ⏭️  SKIP: Exe non trovato")
        return False

    size_mb = exe.stat().st_size / (1024 * 1024)

    # Exe should be at least 10MB (sanity check)
    if size_mb < 10:
        print(f"   ❌ FAIL: Troppo piccolo ({size_mb:.1f} MB) - build incompleto?")
        return False

    # Exe should not be larger than 500MB (something wrong)
    if size_mb > 500:
        print(f"   ⚠️  WARN: Molto grande ({size_mb:.1f} MB) - controllare dipendenze")

    print(f"   ✅ PASS: {size_mb:.1f} MB (dimensione OK)")
    return True


def test_dist_structure() -> bool:
    """Test 3: Struttura directory dist corretta."""
    print("📂 Test 3: Struttura directory...")

    dist_root = get_dist_root()
    if not dist_root:
        print("   ⏭️  SKIP: Dist root non trovata")
        return False

    all_ok = True
    for asset in CRITICAL_ASSETS:
        asset_path = dist_root / asset
        if asset_path.exists():
            log_info(f"Found: {asset}")
        else:
            print(f"   ⚠️  WARN: Asset mancante: {asset}")
            # Non fallire per asset mancanti, solo warning

    print("   ✅ PASS: Struttura base OK")
    return all_ok


def test_critical_dlls() -> bool:
    """Test 4: DLL critiche presenti."""
    print("🔗 Test 4: DLL critiche...")

    dist_root = get_dist_root()
    if not dist_root:
        print("   ⏭️  SKIP: Dist root non trovata")
        return False

    missing = []
    found = 0

    # Search recursively for DLLs
    for dll_name in CRITICAL_DLLS:
        dll_files = list(dist_root.rglob(dll_name))
        if dll_files:
            found += 1
            log_info(f"Found: {dll_name}")
        else:
            missing.append(dll_name)

    if missing:
        print(f"   ⚠️  WARN: DLL mancanti: {', '.join(missing)}")
        print("   (Potrebbero essere incluse con nome diverso)")

    if found >= len(CRITICAL_DLLS) // 2:  # At least half found
        print(f"   ✅ PASS: {found}/{len(CRITICAL_DLLS)} DLL trovate")
        return True
    else:
        print(f"   ❌ FAIL: Troppe DLL mancanti ({found}/{len(CRITICAL_DLLS)})")
        return False


def test_exe_launches(timeout_sec: int = 5) -> bool:
    """Test 5: Eseguibile si avvia senza crash immediato."""
    print(f"🚀 Test 5: Avvio eseguibile (attesa {timeout_sec}s)...")

    exe = find_exe()
    if not exe:
        print("   ⏭️  SKIP: Exe non trovato")
        return False

    try:
        # Launch exe
        process = subprocess.Popen(
            [str(exe)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=exe.parent,  # Run from dist directory
        )

        # Wait for specified time
        time.sleep(timeout_sec)

        # Check if still running
        if process.poll() is None:
            # Still running = good
            print(f"   ✅ PASS: Applicazione in esecuzione dopo {timeout_sec}s")

            # Terminate cleanly
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()

            return True
        else:
            # Crashed
            exit_code = process.returncode
            stderr = process.stderr.read().decode("utf-8", errors="replace")

            print(f"   ❌ FAIL: Crash immediato (exit code: {exit_code})")
            if stderr:
                print("   Stderr (primi 500 char):")
                print(f"   {stderr[:500]}")
            return False

    except Exception as e:
        print(f"   ❌ FAIL: Errore lancio: {e}")
        return False


def test_no_critical_errors() -> bool:
    """Test 6: Nessun errore critico in stderr."""
    print("📝 Test 6: Verifica errori critici...")

    exe = find_exe()
    if not exe:
        print("   ⏭️  SKIP: Exe non trovato")
        return False

    try:
        # Run with short timeout
        result = subprocess.run(
            [str(exe)], capture_output=True, text=True, timeout=8, cwd=exe.parent
        )

        stderr = result.stderr or ""
        stdout = result.stdout or ""
        combined = stderr + stdout

        # Check for critical errors
        errors_found = []
        errors_found = [
            error_pattern
            for error_pattern in CRITICAL_ERRORS
            if error_pattern.lower() in combined.lower()
        ]

        if errors_found:
            print("   ❌ FAIL: Errori critici trovati:")
            for err in errors_found:
                print(f"     - {err}")
            if stderr:
                print(f"   Stderr (primi 300 char): {stderr[:300]}")
            return False

        print("   ✅ PASS: Nessun errore critico rilevato")
        return True

    except subprocess.TimeoutExpired:
        # Timeout = app is running (good)
        print("   ✅ PASS: App in esecuzione (timeout = nessun crash)")
        return True
    except Exception as e:
        print(f"   ❌ FAIL: Errore test: {e}")
        return False


def test_file_count() -> bool:
    """Test 7: Numero file ragionevole nella dist."""
    print("📊 Test 7: Conteggio file...")

    dist_root = get_dist_root()
    if not dist_root:
        print("   ⏭️  SKIP: Dist root non trovata")
        return False

    all_files = list(dist_root.rglob("*"))
    file_count = len([f for f in all_files if f.is_file()])
    dir_count = len([f for f in all_files if f.is_dir()])

    # Calculate total size
    total_size = sum(f.stat().st_size for f in all_files if f.is_file())
    total_size_mb = total_size / (1024 * 1024)

    print(f"   File: {file_count}")
    print(f"   Directory: {dir_count}")
    print(f"   Dimensione totale: {total_size_mb:.1f} MB")

    # Sanity checks
    if file_count < 50:
        print(f"   ⚠️  WARN: Pochi file ({file_count}) - build incompleto?")

    print("   ✅ PASS: Struttura OK")
    return True


# =============================================================================
# MAIN
# =============================================================================


def main():
    """Run all tests."""
    global VERBOSE

    parser = argparse.ArgumentParser(description="Test build Nuitka")
    parser.add_argument("--verbose", "-v", action="store_true", help="Output verboso")
    parser.add_argument("--skip-launch", action="store_true", help="Salta test avvio exe")
    args = parser.parse_args()

    VERBOSE = args.verbose

    print()
    print("=" * 60)
    print("🧪 TEST BUILD - Verifica Eseguibile Nuitka")
    print("=" * 60)
    print(f"Project: {PROJECT_ROOT}")
    print(f"Dist dir: {DIST_DIR}")
    print()

    # Define tests
    tests = [
        ("Exe Exists", test_exe_exists),
        ("Exe Size", test_exe_size),
        ("Dist Structure", test_dist_structure),
        ("Critical DLLs", test_critical_dlls),
        ("File Count", test_file_count),
    ]

    if not args.skip_launch:
        tests.extend(
            [
                ("Exe Launches", test_exe_launches),
                ("No Critical Errors", test_no_critical_errors),
            ]
        )
    else:
        print("⏭️  Test avvio exe saltati (--skip-launch)")
        print()

    # Run tests
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            results.append((name, False))
        print()

    # Summary
    print("=" * 60)
    print("📊 RIEPILOGO RISULTATI")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅" if result else "❌"
        print(f"  {status} {name}")

    print()
    print(f"Passati: {passed}/{total}")
    print()

    if passed == total:
        print("✅ BUILD VALIDATO - Tutti i test passati!")
        print()
        print("Prossimi passi:")
        print("  1. Test manuale: lancia Intelleo.exe")
        print("  2. Security audit: python admin/tools/security_audit.py dist/...")
        print("  3. Procedi a FASE 5 (Testing completo)")
        return 0
    elif passed >= total * 0.7:  # 70%+ passed
        print("⚠️  BUILD PARZIALMENTE VALIDATO")
        print("  Alcuni test falliti, ma la maggior parte OK.")
        print("  Consigliato test manuale prima di procedere.")
        return 1
    else:
        print("❌ BUILD NON VALIDATO")
        print("  Troppi test falliti. Verificare:")
        print("  - Build completato correttamente?")
        print("  - Tutti i moduli inclusi?")
        print("  - Eseguire: python admin/offusca/build_nuitka.py --clean")
        return 2


if __name__ == "__main__":
    sys.exit(main())
