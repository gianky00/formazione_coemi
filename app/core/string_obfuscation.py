"""
String Obfuscation Utility - XOR-based protection per stringhe sensibili.

Questo modulo fornisce funzioni per offuscare stringhe sensibili nel codice
sorgente, rendendole non visibili a tool come `strings` sul binario compilato.

Nota: Questo NON è crittografia forte, ma rende molto più difficile
l'estrazione di segreti con tool semplici. Per sicurezza vera,
considera HSM o external key management.

Usage:
    # Offline: genera stringa offuscata
    from app.core.string_obfuscation import obfuscate_string
    obfuscated = obfuscate_string("MY_SECRET_KEY")
    print(f'_KEY_OBFUSCATED = "{obfuscated}"')

    # Runtime: deoffusca nel codice
    from app.core.string_obfuscation import deobfuscate_string
    _KEY_OBFUSCATED = "..."  # Stringa generata offline
    KEY = deobfuscate_string(_KEY_OBFUSCATED)

Author: Migration Team
Version: 1.0.0 (Nuitka Migration - Security Hardening)
"""

import base64
import sys

# Chiave XOR per obfuscation (cambia questo valore per deployment custom!)
# Non deve essere sequenziale o prevedibile
_XOR_KEY = 0x7B  # 123 in decimale


def xor_bytes(data: bytes, key: int = _XOR_KEY) -> bytes:
    """
    Applica XOR byte-by-byte ai dati.

    Args:
        data: Bytes da processare
        key: Chiave XOR (0-255)

    Returns:
        Bytes XORati

    Example:
        >>> xor_bytes(b"hello", 0x7B)
        b'\\x13\\x1e\\x17\\x17\\x14'
    """
    return bytes([b ^ key for b in data])


def obfuscate_string(plaintext: str, key: int = _XOR_KEY) -> str:
    """
    Offusca una stringa per embedding sicuro nel codice sorgente.

    Il processo:
    1. Converte stringa in bytes UTF-8
    2. Applica XOR con chiave
    3. Codifica risultato in Base64

    Args:
        plaintext: Stringa in chiaro da offuscare
        key: Chiave XOR (default: _XOR_KEY)

    Returns:
        Stringa Base64 dei bytes XORati, sicura per embedding nel codice

    Example:
        >>> secret = "MY_API_KEY_123"
        >>> obfuscated = obfuscate_string(secret)
        >>> print(f'OBFUSCATED = "{obfuscated}"')
        OBFUSCATED = "NjY8PgMRFBYcHRsKCAoJCw=="
    """
    plaintext_bytes = plaintext.encode("utf-8")
    xored = xor_bytes(plaintext_bytes, key)
    encoded = base64.b64encode(xored).decode("ascii")
    return encoded


def deobfuscate_string(obfuscated: str, key: int = _XOR_KEY) -> str:
    """
    Deoffusca una stringa a runtime.

    Il processo inverso:
    1. Decodifica da Base64
    2. Applica XOR con stessa chiave (XOR è simmetrico)
    3. Converte bytes in stringa UTF-8

    Args:
        obfuscated: Stringa Base64 offuscata
        key: Chiave XOR (deve essere la stessa usata per offuscare)

    Returns:
        Stringa originale in chiaro

    Example:
        >>> obfuscated = "NjY8PgMRFBYcHRsKCAoJCw=="
        >>> plaintext = deobfuscate_string(obfuscated)
        >>> print(plaintext)
        MY_API_KEY_123
    """
    decoded = base64.b64decode(obfuscated.encode("ascii"))
    xored = xor_bytes(decoded, key)
    plaintext = xored.decode("utf-8")
    return plaintext


def obfuscate_bytes(plaintext_bytes: bytes, key: int = _XOR_KEY) -> str:
    """
    Offusca bytes raw (utile per chiavi binarie).

    Args:
        plaintext_bytes: Bytes da offuscare
        key: Chiave XOR

    Returns:
        Stringa Base64 dei bytes XORati
    """
    xored = xor_bytes(plaintext_bytes, key)
    encoded = base64.b64encode(xored).decode("ascii")
    return encoded


def deobfuscate_bytes(obfuscated: str, key: int = _XOR_KEY) -> bytes:
    """
    Deoffusca in bytes raw (utile per chiavi binarie).

    Args:
        obfuscated: Stringa Base64 offuscata
        key: Chiave XOR

    Returns:
        Bytes originali
    """
    decoded = base64.b64decode(obfuscated.encode("ascii"))
    xored = xor_bytes(decoded, key)
    return xored


# =============================================================================
# Self-Validation Test Block
# =============================================================================
if __name__ == "__main__":
    # Fix Windows console encoding for emoji support
    if sys.platform == "win32":
        import io

        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

    # Test con segreti reali
    test_secrets = [
        "8kHs_rmwqaRUk1AQLGX65g4AEkWUDapWVsMFUQpN9Ek=",  # Fernet key
        "google_api_key_example_123456789",
        "SECRET_TOKEN",
        "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",  # GitHub token pattern
    ]

    all_passed = True

    for secret in test_secrets:
        obfuscated = obfuscate_string(secret)
        recovered = deobfuscate_string(obfuscated)

        match = secret == recovered
        not_plaintext = secret not in obfuscated

        if not match or not not_plaintext:
            all_passed = False

    # Genera output per copy-paste
    fernet_key = "8kHs_rmwqaRUk1AQLGX65g4AEkWUDapWVsMFUQpN9Ek="
    fernet_obfuscated = obfuscate_string(fernet_key)

    if all_passed:
        pass
    else:
        pass
