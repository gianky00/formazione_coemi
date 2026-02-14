"""
Valida la documentazione cercando riferimenti obsoleti e link rotti.

Verifica che la migrazione PyInstaller → Nuitka sia riflessa
correttamente in tutti i file di documentazione.

Usage:
    python admin/tools/validate_docs.py [--strict]

Author: Migration Team
Version: 1.0.0
"""

import argparse
import re
import sys
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
DOCS_DIR = PROJECT_ROOT / "docs"

# Terms that should NOT appear (or only in specific contexts)
OBSOLETE_TERMS = [
    "pyinstaller",
    "sys._meipass",
    "build_dist.py",
    ".spec file",
    "hidden_imports",
    "hiddenimports",
]

# Exceptions: files/contexts where obsolete terms are acceptable
EXCEPTIONS = {
    "FASE_2_REPORT.md": ["sys._meipass", "pyinstaller"],  # Migration report context
    "FASE_5_REPORT.md": ["pyinstaller"],  # Benchmark comparison
    "FASE_7_REPORT.md": ["pyinstaller", "build_dist.py"],  # Final report comparison
    "MIGRATION_NOTES.md": ["pyinstaller", "sys._meipass", "build_dist.py"],  # Comparison context
    "BUILD_INSTRUCTIONS.md": ["pyinstaller", "build_dist.py"],  # "Replaces PyInstaller" context
    "SYSTEM_ARCHITECTURE.md": ["pyinstaller", "sys._meipass"],  # Comparison/legacy context
    "SYSTEM_DESIGN_REPORT.md": ["sys._meipass", "pyinstaller"],  # Legacy fallback context
    "PROJECT_STRUCTURE_AND_TESTS.md": ["build_dist.py", "pyinstaller"],  # Legacy note
}


# =============================================================================
# CHECKS
# =============================================================================


def check_obsolete_references(strict: bool = False) -> list:
    """
    Cerca riferimenti obsoleti nei file .md

    Args:
        strict: Se True, ignora le eccezioni

    Returns:
        list: Findings con file, linea, termine, contesto
    """
    findings = []

    # Check docs/ directory
    md_files = list(DOCS_DIR.glob("*.md"))

    # Also check root .md files
    md_files.extend(PROJECT_ROOT.glob("*.md"))

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        file_name = md_file.name
        lines = content.split("\n")

        for term in OBSOLETE_TERMS:
            # Check if this term is excepted for this file
            if not strict:
                file_exceptions = EXCEPTIONS.get(file_name, [])
                if term.lower() in [e.lower() for e in file_exceptions]:
                    continue

            # Search for term in content
            for i, line in enumerate(lines, 1):
                if term.lower() in line.lower():
                    findings.append(
                        {"file": file_name, "line": i, "term": term, "context": line.strip()[:80]}
                    )

    return findings


def check_broken_links() -> list:
    """
    Verifica link interni rotti nei file markdown.

    Returns:
        list: Broken links con file, link text, target
    """
    broken = []

    md_files = list(DOCS_DIR.glob("*.md"))
    md_files.extend(PROJECT_ROOT.glob("*.md"))

    for md_file in md_files:
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue

        # Find markdown links: [text](path)
        links = re.findall(r"\[([^\]]+)\]\(([^)]+)\)", content)

        for text, link in links:
            # Skip external links, anchors, and mailto
            if link.startswith("http") or link.startswith("#") or link.startswith("mailto:"):
                continue

            # Remove anchor from link if present
            link_path = link.split("#")[0]
            if not link_path:
                continue

            # Try multiple resolution strategies
            targets_to_try = [
                md_file.parent / link_path,  # Relative to file
                PROJECT_ROOT / link_path,  # Relative to project root
                DOCS_DIR / link_path,  # Relative to docs/
            ]

            found = False
            for target in targets_to_try:
                if target.exists():
                    found = True
                    break

            if not found:
                broken.append({"file": md_file.name, "link": link, "text": text})

    return broken


def check_required_sections() -> list:
    """
    Verifica che BUILD_INSTRUCTIONS.md contenga sezioni chiave.

    Returns:
        list: Missing sections
    """
    missing = []

    build_docs = DOCS_DIR / "BUILD_INSTRUCTIONS.md"
    if not build_docs.exists():
        return [{"file": "BUILD_INSTRUCTIONS.md", "issue": "File non trovato"}]

    content = build_docs.read_text(encoding="utf-8").lower()

    required_sections = [
        "build_nuitka.py",
        "nuitka",
        "--clean",
        "--fast",
        "dist/nuitka",
    ]

    missing = [
        {"file": "BUILD_INSTRUCTIONS.md", "missing": section}
        for section in required_sections
        if section.lower() not in content
    ]

    return missing


# =============================================================================
# MAIN
# =============================================================================


def main():
    parser = argparse.ArgumentParser(description="Valida documentazione migrazione")
    parser.add_argument("--strict", action="store_true", help="Ignora eccezioni")
    args = parser.parse_args()

    print()
    print("=" * 60)
    print("🔍 VALIDAZIONE DOCUMENTAZIONE")
    print("=" * 60)
    print(f"   Docs dir: {DOCS_DIR}")
    print()

    issues_found = False

    # Check 1: Riferimenti obsoleti
    print("1. Cerca riferimenti obsoleti...")
    obsolete = check_obsolete_references(strict=args.strict)

    if obsolete:
        print(f"   ⚠️  Trovati {len(obsolete)} riferimenti obsoleti:")
        for finding in obsolete[:10]:
            print(f"      - {finding['file']}:{finding['line']}: '{finding['term']}'")
            print(f"        {finding['context'][:60]}...")
        if len(obsolete) > 10:
            print(f"      ... e altri {len(obsolete) - 10}")
        issues_found = True
    else:
        print("   ✅ Nessun riferimento obsoleto")

    print()

    # Check 2: Link rotti
    print("2. Verifica link interni...")
    broken = check_broken_links()

    if broken:
        print(f"   ⚠️  Trovati {len(broken)} link rotti:")
        for link in broken[:10]:
            print(f"      - {link['file']}: [{link['text']}]({link['link']})")
        issues_found = True
    else:
        print("   ✅ Nessun link rotto")

    print()

    # Check 3: Sezioni richieste
    print("3. Verifica sezioni BUILD_INSTRUCTIONS.md...")
    missing = check_required_sections()

    if missing:
        print("   ⚠️  Sezioni mancanti:")
        for item in missing:
            if "missing" in item:
                print(f"      - Manca: '{item['missing']}'")
            else:
                print(f"      - {item['issue']}")
        issues_found = True
    else:
        print("   ✅ Tutte le sezioni presenti")

    print()
    print("=" * 60)

    if issues_found:
        print("⚠️  DOCUMENTAZIONE RICHIEDE AGGIORNAMENTI")
        print()
        print("   Nota: Alcuni riferimenti 'obsoleti' potrebbero essere")
        print("   intenzionali (es. confronti, note legacy).")
        print("   Usa --strict per controllo rigoroso.")
        return 1
    else:
        print("✅ DOCUMENTAZIONE VALIDATA")
        print()
        print("   Tutti i controlli passati:")
        print("   - Nessun riferimento PyInstaller non contestualizzato")
        print("   - Nessun link interno rotto")
        print("   - BUILD_INSTRUCTIONS.md aggiornato per Nuitka")
        return 0


if __name__ == "__main__":
    sys.exit(main())
