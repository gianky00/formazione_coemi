"""
Benchmark comparativo PyInstaller vs Nuitka.

Misura tempo di avvio (da lancio a backend ready) per confrontare
le performance tra build PyInstaller e Nuitka.

Usage:
    python admin/tools/benchmark_builds.py [--runs=5]

Author: Migration Team
Version: 1.0.0
"""
import subprocess
import sys
import time
import argparse
from pathlib import Path
from typing import List, Optional

# Fix Windows console encoding
if sys.platform == "win32":
    import io
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
    except Exception:
        pass

# =============================================================================
# CONFIGURATION
# =============================================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

# Build paths
NUITKA_EXE = PROJECT_ROOT / "dist" / "nuitka" / "Intelleo.dist" / "Intelleo.exe"
PYINSTALLER_EXE = PROJECT_ROOT / "dist" / "Intelleo" / "Intelleo.exe"

# API health endpoint
API_HEALTH = "http://localhost:8000/api/v1/health"

# Default runs
DEFAULT_RUNS = 5


# =============================================================================
# BENCHMARK
# =============================================================================

def wait_for_backend(timeout: int = 30) -> bool:
    """Wait for backend to respond."""
    try:
        import requests
    except ImportError:
        return False
    
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = requests.get(API_HEALTH, timeout=1)
            if response.status_code == 200:
                return True
        except:
            pass
        time.sleep(0.3)
    return False


def benchmark_startup(exe_path: Path, runs: int = 5) -> List[float]:
    """
    Misura tempo di avvio (fino a backend ready).
    
    Args:
        exe_path: Path to executable
        runs: Number of runs
        
    Returns:
        list: Times in seconds
    """
    times = []
    
    for i in range(runs):
        print(f"  Run {i+1}/{runs}...", end=" ", flush=True)
        
        start = time.time()
        process = subprocess.Popen(
            [str(exe_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=exe_path.parent
        )
        
        # Wait for backend
        backend_ready = wait_for_backend(timeout=30)
        elapsed = time.time() - start
        
        # Cleanup
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        if backend_ready:
            times.append(elapsed)
            print(f"{elapsed:.2f}s ✅")
        else:
            print(f"TIMEOUT ❌")
        
        # Pause between runs
        time.sleep(2)
    
    return times


def main():
    parser = argparse.ArgumentParser(description="Benchmark PyInstaller vs Nuitka")
    parser.add_argument("--runs", type=int, default=DEFAULT_RUNS, help="Number of runs")
    args = parser.parse_args()
    
    try:
        import requests
    except ImportError:
        print("❌ Modulo 'requests' richiesto: pip install requests")
        return 1
    
    print("\n" + "=" * 70)
    print("📊 BENCHMARK - PyInstaller vs Nuitka")
    print("=" * 70 + "\n")
    
    results = {}
    
    # Benchmark Nuitka
    if NUITKA_EXE.exists():
        print(f"🚀 Benchmark Nuitka ({args.runs} runs)...")
        print(f"   Path: {NUITKA_EXE}")
        times = benchmark_startup(NUITKA_EXE, runs=args.runs)
        if times:
            avg = sum(times) / len(times)
            results["Nuitka"] = {"times": times, "avg": avg, "min": min(times), "max": max(times)}
            print(f"   Media: {avg:.2f}s | Min: {min(times):.2f}s | Max: {max(times):.2f}s\n")
    else:
        print(f"⚠️  Nuitka build non trovato: {NUITKA_EXE}\n")
    
    # Benchmark PyInstaller
    if PYINSTALLER_EXE.exists():
        print(f"📦 Benchmark PyInstaller ({args.runs} runs)...")
        print(f"   Path: {PYINSTALLER_EXE}")
        times = benchmark_startup(PYINSTALLER_EXE, runs=args.runs)
        if times:
            avg = sum(times) / len(times)
            results["PyInstaller"] = {"times": times, "avg": avg, "min": min(times), "max": max(times)}
            print(f"   Media: {avg:.2f}s | Min: {min(times):.2f}s | Max: {max(times):.2f}s\n")
    else:
        print(f"⚠️  PyInstaller build non trovato: {PYINSTALLER_EXE}\n")
    
    # Comparison
    print("=" * 70)
    print("📈 RISULTATI")
    print("=" * 70)
    
    if not results:
        print("❌ Nessun build trovato per benchmark")
        return 1
    
    for name, data in results.items():
        print(f"\n{name}:")
        print(f"  Media:   {data['avg']:.2f}s")
        print(f"  Min:     {data['min']:.2f}s")
        print(f"  Max:     {data['max']:.2f}s")
    
    if len(results) == 2:
        nuitka_avg = results["Nuitka"]["avg"]
        pyinst_avg = results["PyInstaller"]["avg"]
        
        if pyinst_avg > 0:
            improvement = ((pyinst_avg - nuitka_avg) / pyinst_avg) * 100
            
            print("\n" + "-" * 70)
            print(f"   PyInstaller: {pyinst_avg:.2f}s")
            print(f"   Nuitka:      {nuitka_avg:.2f}s")
            print(f"   Differenza:  {abs(pyinst_avg - nuitka_avg):.2f}s")
            
            if improvement > 0:
                print(f"\n   ✅ Nuitka è {improvement:.1f}% PIÙ VELOCE")
            else:
                print(f"\n   ⚠️  PyInstaller è {abs(improvement):.1f}% più veloce")
    
    print("\n" + "=" * 70)
    return 0


if __name__ == "__main__":
    sys.exit(main())

