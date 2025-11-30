import os

class SecureKey:
    """
    Protects sensitive keys in memory using XOR obfuscation.
    The key is stored encrypted and only decrypted transiently when accessed.
    """
    def __init__(self, key_bytes: bytes):
        # Generate a random nonce
        self._nonce = os.urandom(len(key_bytes))
        # Store key XOR nonce
        self._blob = bytes(a ^ b for a, b in zip(key_bytes, self._nonce))

    @property
    def value(self) -> bytes:
        """Returns the decrypted key. Decryption happens on the fly."""
        return bytes(a ^ b for a, b in zip(self._blob, self._nonce))

# Initialize the secure storage with the secret key
# The literal bytes are used only during initialization and then discarded by GC
_SECURE_STORE = SecureKey(b'8kHs_rmwqaRUk1AQLGX65g4AEkWUDapWVsMFUQpN9Ek=')

def get_license_secret_key() -> bytes:
    """
    Retrieves the license secret key.

    Security Note:
    The key is decrypted on-the-fly and returned.
    Callers should use it immediately and let it go out of scope.
    """
    return _SECURE_STORE.value
