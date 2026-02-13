"""
Stress Test - Avvii multipli per verificare stabilità.

Esegue N avvii consecutivi dell'applicazione per rilevare crash
intermittenti e problemi di stabilità.

Usage:
    python admin/tools/stress_test.py [--runs=100] [--delay=1]

Author: Migration Team
Version: 1.0.0
"""

import argparse
import subprocess
import sys
import time
from datetime import datetime
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

# Possible exe locations
EXE_CANDIDATES = [
    DIST_DIR / "Intelleo.dist" / "Intelleo.exe",
    DIST_DIR / "launcher.dist" / "Intelleo.exe",
    DIST_DIR / "Intelleo.exe",
]

# Defaults
DEFAULT_RUNS = 100
DEFAULT_DELAY = 1  # seconds between runs
WAIT_TIME = 3  # seconds to wait after launch


# =============================================================================
# HELPERS
# =============================================================================


def find_exe() -> Path:
    """Find the compiled executable."""
    for candidate in EXE_CANDIDATES:
        if candidate.exists():
            return candidate
    return None


# =============================================================================
# STRESS TEST
# =============================================================================


def run_stress_test(exe_path: Path, runs: int, delay: float):
    """
    Run stress test: multiple consecutive launches.

    Args:
        exe_path: Path to executable
        runs: Number of runs
        delay: Delay between runs (seconds)
    """
    print(f"\n🔥 STRESS TEST - {runs} avvii consecutivi\n")
    print(f"   Exe: {exe_path}")
    print(f"   Wait time: {WAIT_TIME}s per avvio")
    print(f"   Delay: {delay}s tra avvii")
    print()

    crashes = 0
    success = 0
    errors = []

    start_time = time.time()

    for i in range(runs):
        run_num = i + 1
        print(f"Run {run_num:3d}/{runs}...", end=" ", flush=True)

        try:
            process = subprocess.Popen(
                [str(exe_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=exe_path.parent
            )

            # Wait for app to stabilize
            time.sleep(WAIT_TIME)

            # Check if still running
            if process.poll() is None:
                print("✅")
                success += 1

                # Cleanup
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            else:
                exit_code = process.returncode
                stderr = process.stderr.read().decode("utf-8", errors="replace")[:200]
                print(f"❌ CRASH (exit: {exit_code})")
                crashes += 1
                errors.append({"run": run_num, "exit_code": exit_code, "stderr": stderr})

        except Exception as e:
            print(f"❌ ERROR: {e}")
            crashes += 1
            errors.append({"run": run_num, "error": str(e)})

        # Delay between runs
        if i < runs - 1:
            time.sleep(delay)

    elapsed = time.time() - start_time

    # Report
    print()
    print("=" * 60)
    print("📊 RISULTATI STRESS TEST")
    print("=" * 60)
    print(f"\n   Totale avvii:  {runs}")
    print(f"   Successi:      {success}")
    print(f"   Crash:         {crashes}")
    print(f"   Success Rate:  {(success / runs) * 100:.1f}%")
    print(f"   Tempo totale:  {elapsed / 60:.1f} minuti")

    if errors:
        print("\n   ⚠️  Dettagli crash:")
        for err in errors[:5]:  # Show first 5
            print(f"      Run {err['run']}: {err.get('exit_code', err.get('error', 'unknown'))}")
        if len(errors) > 5:
            print(f"      ... e altri {len(errors) - 5} errori")

    print()
    if crashes == 0:
        print("✅ STRESS TEST PASSATO - Nessun crash rilevato")
        return 0
    elif crashes / runs < 0.01:  # < 1% crash rate
        print(f"⚠️  STRESS TEST PARZIALE - {crashes} crash ({crashes / runs * 100:.2f}%)")
        return 1
    else:
        print(f"❌ STRESS TEST FALLITO - Troppi crash ({crashes / runs * 100:.1f}%)")
        return 2


def main():
    parser = argparse.ArgumentParser(
        description="Stress test: avvii multipli consecutivi",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Esempi:
  python stress_test.py              # 100 avvii (default)
  python stress_test.py --runs=50    # 50 avvii
  python stress_test.py --delay=2    # 2s tra avvii
        """,
    )
    parser.add_argument(
        "--runs", type=int, default=DEFAULT_RUNS, help=f"Numero avvii (default: {DEFAULT_RUNS})"
    )
    parser.add_argument(
        "--delay",
        type=float,
        default=DEFAULT_DELAY,
        help=f"Delay tra avvii in secondi (default: {DEFAULT_DELAY})",
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("🔥 STRESS TEST - Stabilità Build Nuitka")
    print("=" * 60)
    print(f"   Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Find exe
    exe = find_exe()
    if not exe:
        print(f"\n❌ Build non trovato in: {DIST_DIR}")
        print("   Esegui prima: python admin/offusca/build_nuitka.py")
        return 1

    # Confirm with user for long tests
    estimated_time = args.runs * (WAIT_TIME + args.delay) / 60
    print(f"\n   ⏱️  Tempo stimato: ~{estimated_time:.0f} minuti")

    if args.runs > 20:
        print(f"\n   ⚠️  Test lungo ({args.runs} avvii). Premi Ctrl+C per interrompere.\n")
        time.sleep(2)

    return run_stress_test(exe, args.runs, args.delay)


if __name__ == "__main__":
    sys.exit(main())
