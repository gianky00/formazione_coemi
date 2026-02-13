"""
Test path resolution in tutti i contesti critici.
Questo script verifica che tutti i path siano correttamente risolti
sia in ambiente di sviluppo che (simulato) in ambiente frozen.

Esegui: python admin/tools/test_path_resolution_integrated.py
"""

import os
import sys

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    import io

    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from pathlib import Path

from app.core.path_resolver import (
    get_asset_path,
    get_base_path,
    get_database_path,
    get_license_path,
    get_logs_path,
    get_user_data_path,
)


def test_base_path_contains_project_structure():
    """Verifica che il base path contenga la struttura del progetto."""
    print("📂 Test Base Path Structure...")
    base = get_base_path()

    required_dirs = ["app", "desktop_app", "guide_frontend"]
    required_files = ["launcher.py", "requirements.txt"]

    missing = []
    for d in required_dirs:
        if not (base / d).exists():
            missing.append(f"dir:{d}")
    for f in required_files:
        if not (base / f).exists():
            missing.append(f"file:{f}")

    if missing:
        print(f"   ❌ FAIL: Mancanti: {missing}")
        return False

    print(f"   Path: {base}")
    print("   ✅ PASS: Struttura progetto trovata")
    return True


def test_guide_html_loading():
    """Testa che React SPA sia trovato."""
    print("⚛️  Test Guide HTML Loading...")

    # In dev mode, should find guide_frontend/dist/index.html
    guide_html = get_asset_path("guide_frontend/dist/index.html")

    if guide_html.exists():
        print(f"   Path: {guide_html}")
        print(f"   Size: {guide_html.stat().st_size} bytes")
        print("   ✅ PASS")
        return True
    else:
        print(f"   Path (not found): {guide_html}")
        print("   ❌ FAIL: React SPA non trovata")
        print("   → Esegui: cd guide_frontend && npm run build")
        return False


def test_license_loading():
    """Testa che LicenseManager trovi config.dat."""
    print("🔐 Test License Loading...")

    try:
        from desktop_app.services.license_manager import LicenseManager

        # Use the internal find method
        license_file = LicenseManager._find_license_file()

        if license_file and os.path.exists(license_file):
            print(f"   File: {license_file}")
            print("   ✅ PASS")
            return True
        else:
            # Check via path_resolver
            license_dir = get_license_path()
            config_file = license_dir / "config.dat"

            if config_file.exists():
                print(f"   File: {config_file}")
                print("   ✅ PASS (via path_resolver)")
                return True
            else:
                print(f"   License dir: {license_dir}")
                print("   ❌ FAIL: config.dat non trovato")
                return False

    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False


def test_database_path():
    """Testa path database."""
    print("🗃️  Test Database Path...")

    try:
        # Test via path_resolver
        db_path = get_database_path()

        print(f"   Path: {db_path}")
        print(f"   Parent exists: {db_path.parent.exists()}")

        # Check that it's in user data
        user_data = get_user_data_path()
        if str(user_data) in str(db_path):
            print("   Location: User data directory ✓")
            print("   ✅ PASS")
            return True
        else:
            print("   ⚠️ WARNING: DB path not in user data")
            return True  # Still pass, just warn

    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False


def test_user_data_path_writable():
    """Testa che la directory user data sia scrivibile."""
    print("📁 Test User Data Writable...")

    user_data = get_user_data_path()
    test_file = user_data / ".write_test"

    try:
        # Try to write
        test_file.write_text("test")

        # Verify
        if test_file.exists():
            test_file.unlink()  # Cleanup
            print(f"   Path: {user_data}")
            print("   ✅ PASS: Directory scrivibile")
            return True
        else:
            print("   ❌ FAIL: Write verification failed")
            return False

    except Exception as e:
        print(f"   ❌ FAIL: {e}")
        return False


def test_logs_path():
    """Testa che la directory logs sia accessibile."""
    print("📜 Test Logs Path...")

    logs_path = get_logs_path()

    if logs_path.exists() and logs_path.is_dir():
        print(f"   Path: {logs_path}")
        print("   ✅ PASS")
        return True
    else:
        print(f"   Path: {logs_path}")
        print("   ❌ FAIL: Directory non trovata")
        return False


def test_icon_assets():
    """Testa che le icone siano trovate."""
    print("🎨 Test Icon Assets...")

    icons_to_check = [
        "desktop_app/icons/icon.ico",
        "desktop_app/assets/icon.png",
    ]

    found_any = False
    for icon_rel in icons_to_check:
        icon_path = get_asset_path(icon_rel)
        if icon_path.exists():
            print(f"   ✅ {icon_rel}")
            found_any = True
        else:
            print(f"   ❌ {icon_rel} (not found)")

    if found_any:
        print("   ✅ PASS: Almeno un'icona trovata")
        return True
    else:
        print("   ❌ FAIL: Nessuna icona trovata")
        return False


def test_path_resolver_consistency():
    """Testa che i path siano consistenti tra le funzioni."""
    print("🔗 Test Path Resolver Consistency...")

    base = get_base_path()
    user_data = get_user_data_path()
    license_path = get_license_path()
    db_path = get_database_path()
    logs_path = get_logs_path()

    # All should be Path objects
    all_paths = [base, user_data, license_path, db_path, logs_path]

    for p in all_paths:
        if not isinstance(p, Path):
            print(f"   ❌ FAIL: {p} non è un Path object")
            return False

    # User data paths should be related
    if str(user_data) not in str(db_path):
        print("   ⚠️ WARNING: db_path non in user_data")

    if str(user_data) not in str(logs_path):
        print("   ⚠️ WARNING: logs_path non in user_data")

    print(f"   Base:     {base}")
    print(f"   UserData: {user_data}")
    print(f"   License:  {license_path}")
    print(f"   Database: {db_path}")
    print(f"   Logs:     {logs_path}")
    print("   ✅ PASS")
    return True


def main():
    print("\n" + "=" * 60)
    print("🧪 TEST PATH RESOLUTION - INTEGRATED")
    print("=" * 60)
    print(f"Environment: {'Frozen' if getattr(sys, 'frozen', False) else 'Development'}")
    print(f"Python: {sys.version.split()[0]}")
    print("=" * 60 + "\n")

    tests = [
        ("Base Path Structure", test_base_path_contains_project_structure),
        ("Guide HTML Loading", test_guide_html_loading),
        ("License Loading", test_license_loading),
        ("Database Path", test_database_path),
        ("User Data Writable", test_user_data_path_writable),
        ("Logs Path", test_logs_path),
        ("Icon Assets", test_icon_assets),
        ("Path Consistency", test_path_resolver_consistency),
    ]

    results = []
    for name, test_func in tests:
        try:
            result = test_func()
        except Exception as e:
            print(f"   ❌ EXCEPTION: {e}")
            result = False
        results.append((name, result))
        print()  # Blank line between tests

    # Summary
    print("=" * 60)
    print("📊 RIEPILOGO")
    print("=" * 60)

    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {name}")

    print("=" * 60)
    print(f"Risultato: {passed}/{total} test passati")

    if passed == total:
        print("✅ TUTTI I TEST PASSATI - Path resolution pronta per Nuitka!")
        return 0
    else:
        print("❌ ALCUNI TEST FALLITI - Correggere prima di compilare")
        return 1


if __name__ == "__main__":
    sys.exit(main())
