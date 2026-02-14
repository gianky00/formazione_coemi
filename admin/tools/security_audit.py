"""
Security Audit Tool - Verifica che nessun segreto sia esposto nel binario.

Questo tool scansiona un file eseguibile compilato alla ricerca di stringhe
sensibili che non dovrebbero essere visibili (chiavi API, token, etc.).

Usage:
    python admin/tools/security_audit.py <binary_path>
    python admin/tools/security_audit.py dist/Intelleo.exe

Exit codes:
    0 - Audit passed (no secrets found)
    1 - Audit failed (secrets exposed)
    2 - Error (file not found, etc.)

Author: Migration Team
Version: 1.0.0 (Nuitka Migration - Security Hardening)
"""

import contextlib
import io
import os
import re
import shutil
import subprocess
import sys

# Fix Windows console encoding for emoji support
if sys.platform == "win32":
    with contextlib.suppress(Exception):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")


# Stringhe che NON devono apparire nel binario compilato
FORBIDDEN_STRINGS = [
    # Fernet key (la nostra chiave di licenza)
    "8kHs_rmwqaRUk1AQLGX65g4AEkWUDapWVsMFUQpN9Ek",
    # API key prefixes
    "AIzaSy",  # Google API keys prefix
    "ghp_",  # GitHub Personal Access Token prefix
    "gho_",  # GitHub OAuth Token prefix
    "sk-",  # OpenAI API key prefix
    "sk_live_",  # Stripe live key prefix
    # Common sensitive patterns
    "PRIVATE_KEY",
    "BEGIN RSA PRIVATE",
    "BEGIN OPENSSH PRIVATE",
]

# Stringhe che sono OK (false positives)
ALLOWED_PATTERNS = [
    "Fernet",  # Library name is OK
    "cryptography",  # Library name is OK
]


def find_strings_tool() -> str | None:
    """
    Trova il tool `strings` disponibile nel sistema.

    Returns:
        Path al tool strings, o None se non trovato
    """
    # Prova `strings` direttamente (Linux, Git Bash)
    if shutil.which("strings"):
        return "strings"

    # Windows: prova in Git Bash paths comuni
    git_paths = [
        r"C:\Program Files\Git\usr\bin\strings.exe",
        r"C:\Program Files (x86)\Git\usr\bin\strings.exe",
    ]

    for path in git_paths:
        if os.path.exists(path):
            return path

    return None


def extract_strings(binary_path: str, min_length: int = 6) -> str:
    """
    Estrae tutte le stringhe leggibili da un binario.

    Args:
        binary_path: Path al file eseguibile
        min_length: Lunghezza minima delle stringhe da estrarre

    Returns:
        Stringa contenente tutte le stringhe estratte
    """
    strings_tool = find_strings_tool()

    if strings_tool:
        # Usa tool `strings` nativo
        result = subprocess.run(
            [strings_tool, "-n", str(min_length), binary_path],
            capture_output=True,
            text=True,
            errors="replace",
            check=False,
        )
        return result.stdout
    else:
        # Fallback: estrazione manuale (più lenta ma funziona ovunque)
        print("⚠️  Tool 'strings' non trovato. Usando estrazione manuale...")
        return _extract_strings_manual(binary_path, min_length)


def _extract_strings_manual(binary_path: str, min_length: int = 6) -> str:
    """
    Estrazione manuale di stringhe (fallback se `strings` non disponibile).
    """
    with open(binary_path, "rb") as f:
        data = f.read()

    # Cerca sequenze di caratteri stampabili
    pattern = rb"[\x20-\x7e]{" + str(min_length).encode() + rb",}"
    matches = re.findall(pattern, data)

    return "\n".join(m.decode("ascii", errors="replace") for m in matches)


def check_strings_in_binary(binary_path: str, forbidden_strings: list[str]) -> dict[str, bool]:
    """
    Cerca stringhe proibite nel binario compilato.

    Args:
        binary_path: Path al .exe
        forbidden_strings: Lista di stringhe che NON devono apparire

    Returns:
        dict: {string: found (bool)}
    """
    print(f"🔍 Scanning {binary_path}...")
    print(f"   File size: {os.path.getsize(binary_path) / 1024 / 1024:.1f} MB")

    # Estrai tutte le stringhe
    all_strings = extract_strings(binary_path)

    print(f"   Extracted strings: {len(all_strings.splitlines())} lines")
    print()

    findings = {}
    for forbidden in forbidden_strings:
        found = forbidden in all_strings
        findings[forbidden] = found

        # Mostra troncato per chiavi lunghe
        display = forbidden[:30] + "..." if len(forbidden) > 30 else forbidden
        status = "❌ FOUND" if found else "✅ NOT FOUND"
        print(f"   {status}: {display}")

    return findings


def audit_source_code(project_root: str) -> dict[str, list[str]]:
    """
    Audit del codice sorgente per stringhe hardcoded.
    """
    print("\n📝 Auditing source code...")

    findings: dict[str, list[str]] = {}
    sensitive_patterns = [
        ("Fernet key", "8kHs_rmwqaRUk1AQLGX65g4AEkWUDapWVsMFUQpN9Ek="),
    ]

    # File da escludere (test, tool di generazione, admin tools, etc.)
    exclude_patterns = [
        "test_",
        "generate_obfuscated",
        "__pycache__",
        ".pyc",
        "security_audit.py",
        "string_obfuscation.py",  # Has test data in __main__ block
        "admin_license_gui.py",  # Admin tool, not distributed
    ]

    # Directories da escludere completamente
    exclude_dirs = [
        "admin",  # Admin tools non distribuiti
        "tests",  # Test files
        ".git",
    ]

    for root, dirs, files in os.walk(project_root):
        # Skip excluded directories
        dirs[:] = [
            d
            for d in dirs
            if not d.startswith(".") and d != "__pycache__" and d not in exclude_dirs
        ]

        for file in files:
            if not file.endswith(".py"):
                continue

            # Skip excluded files
            if any(exc in file for exc in exclude_patterns):
                continue

            filepath = os.path.join(root, file)
            rel_path = os.path.relpath(filepath, project_root)

            with contextlib.suppress(Exception):
                with open(filepath, encoding="utf-8") as f:
                    content = f.read()

                for name, pattern in sensitive_patterns:
                    if pattern in content and (
                        f'"{pattern}"' in content or f"'{pattern}'" in content
                    ):
                        # Check if it's in obfuscated form (OK) or plaintext (BAD)
                        if rel_path not in findings:
                            findings[rel_path] = []
                        findings[rel_path].append(name)
                        print(f"   ⚠️  {rel_path}: {name} found as plaintext!")

    if not findings:
        print("   ✅ No plaintext secrets found in source code")

    return findings


def main() -> None:
    print("\n" + "=" * 70)
    print("🔐 SECURITY AUDIT TOOL - Intelleo")
    print("=" * 70)

    # Check arguments
    binary_path = None
    if len(sys.argv) >= 2:
        binary_path = sys.argv[1]

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))

    # Audit source code first
    source_findings = audit_source_code(project_root)

    # Audit binary if provided
    binary_findings = {}
    if binary_path:
        if not os.path.exists(binary_path):
            print(f"\n❌ ERROR: Binary not found: {binary_path}")
            sys.exit(2)

        print(f"\n🔍 Binary Audit: {binary_path}")
        print("-" * 70)
        binary_findings = check_strings_in_binary(binary_path, FORBIDDEN_STRINGS)
    else:
        print("\n⚠️  No binary specified. Skipping binary audit.")
        print("   Usage: python security_audit.py <path_to_binary>")

    # Summary
    print("\n" + "=" * 70)
    print("📊 AUDIT SUMMARY")
    print("=" * 70)

    source_failed = bool(source_findings)
    binary_failed = any(binary_findings.values()) if binary_findings else False

    print(f"\nSource Code Audit: {'❌ FAILED' if source_failed else '✅ PASSED'}")
    if source_findings:
        for file, issues in source_findings.items():
            print(f"   - {file}: {', '.join(issues)}")

    if binary_path:
        print(f"Binary Audit:      {'❌ FAILED' if binary_failed else '✅ PASSED'}")
        if binary_failed:
            for string, found in binary_findings.items():
                if found:
                    print(f"   - Exposed: {string[:30]}...")

    print("\n" + "=" * 70)

    if source_failed or binary_failed:
        print("❌ SECURITY AUDIT FAILED")
        print("\nActions Required:")
        if source_failed:
            print("1. Replace plaintext secrets with obfuscated versions")
            print("   Run: python admin/tools/generate_obfuscated_keys.py")
        if binary_failed:
            print("2. Rebuild the binary after fixing source code")
        sys.exit(1)
    else:
        print("✅ SECURITY AUDIT PASSED")
        print("\nAll sensitive strings are properly obfuscated.")
        sys.exit(0)


if __name__ == "__main__":
    main()
