"""
Test suite for app.core.string_obfuscation module.

Tests string obfuscation and deobfuscation functionality
used for protecting sensitive strings in compiled binaries.
"""
import pytest
from app.core.string_obfuscation import (
    obfuscate_string, 
    deobfuscate_string,
    xor_bytes,
    obfuscate_bytes,
    deobfuscate_bytes,
    _XOR_KEY
)


class TestXorBytes:
    """Tests for xor_bytes() function."""
    
    def test_xor_bytes_basic(self):
        """Test basic XOR operation."""
        data = b'hello'
        xored = xor_bytes(data)
        
        # XOR is symmetric: XOR twice should return original
        recovered = xor_bytes(xored)
        assert recovered == data
        
    def test_xor_bytes_different_key(self):
        """Test XOR with custom key."""
        data = b'test'
        key = 0x42
        
        xored = xor_bytes(data, key)
        recovered = xor_bytes(xored, key)
        
        assert recovered == data
        
    def test_xor_bytes_changes_data(self):
        """Test that XOR actually changes the data."""
        data = b'secret'
        xored = xor_bytes(data)
        
        assert xored != data


class TestObfuscateString:
    """Tests for obfuscate_string() function."""
    
    def test_obfuscate_deobfuscate_roundtrip(self):
        """Test that obfuscate/deobfuscate is reversible."""
        original = "TEST_SECRET_123"
        obfuscated = obfuscate_string(original)
        recovered = deobfuscate_string(obfuscated)
        
        assert original == recovered
        
    def test_obfuscated_different_from_original(self):
        """Test that obfuscated string is different from original."""
        original = "MY_API_KEY"
        obfuscated = obfuscate_string(original)
        
        assert original != obfuscated
        
    def test_obfuscated_not_plaintext(self):
        """Test that obfuscated string doesn't contain original plaintext."""
        secret = "MY_SECRET_KEY"
        obfuscated = obfuscate_string(secret)
        
        # The obfuscated version should not contain fragments of original
        assert "MY" not in obfuscated
        assert "SECRET" not in obfuscated
        assert "KEY" not in obfuscated
        
    def test_obfuscated_is_base64(self):
        """Test that obfuscated string is valid Base64."""
        import base64
        
        secret = "test_secret"
        obfuscated = obfuscate_string(secret)
        
        # Should not raise exception
        decoded = base64.b64decode(obfuscated)
        assert len(decoded) > 0
        
    def test_empty_string(self):
        """Test handling of empty string."""
        original = ""
        obfuscated = obfuscate_string(original)
        recovered = deobfuscate_string(obfuscated)
        
        assert recovered == original
        
    def test_unicode_string(self):
        """Test handling of unicode characters."""
        original = "Caffè_Naïve_日本語"
        obfuscated = obfuscate_string(original)
        recovered = deobfuscate_string(obfuscated)
        
        assert recovered == original
        
    def test_special_characters(self):
        """Test handling of special characters."""
        original = "key=value&token=abc123!@#$%"
        obfuscated = obfuscate_string(original)
        recovered = deobfuscate_string(obfuscated)
        
        assert recovered == original


class TestObfuscateBytes:
    """Tests for obfuscate_bytes() and deobfuscate_bytes() functions."""
    
    def test_bytes_roundtrip(self):
        """Test bytes obfuscation roundtrip."""
        original = b'binary_secret_data'
        obfuscated = obfuscate_bytes(original)
        recovered = deobfuscate_bytes(obfuscated)
        
        assert recovered == original
        
    def test_binary_data(self):
        """Test with actual binary data (non-UTF8)."""
        original = bytes(range(256))  # All possible byte values
        obfuscated = obfuscate_bytes(original)
        recovered = deobfuscate_bytes(obfuscated)
        
        assert recovered == original


class TestFernetKeyObfuscation:
    """Tests specific to Fernet key obfuscation (production use case)."""
    
    def test_fernet_key_format(self):
        """Test that Fernet key maintains correct format after roundtrip."""
        # Standard Fernet key format (44 chars Base64)
        fernet_key = "8kHs_rmwqaRUk1AQLGX65g4AEkWUDapWVsMFUQpN9Ek="
        
        obfuscated = obfuscate_string(fernet_key)
        recovered = deobfuscate_string(obfuscated)
        
        assert recovered == fernet_key
        assert len(recovered) == 44
        
    def test_fernet_key_usable(self):
        """Test that deobfuscated Fernet key is actually usable."""
        from cryptography.fernet import Fernet
        
        fernet_key = "8kHs_rmwqaRUk1AQLGX65g4AEkWUDapWVsMFUQpN9Ek="
        
        obfuscated = obfuscate_string(fernet_key)
        recovered = deobfuscate_string(obfuscated)
        
        # Should be able to create a Fernet instance
        cipher = Fernet(recovered.encode('ascii'))
        
        # Should be able to encrypt/decrypt
        test_data = b"test message"
        encrypted = cipher.encrypt(test_data)
        decrypted = cipher.decrypt(encrypted)
        
        assert decrypted == test_data


class TestLicenseSecurityIntegration:
    """Integration tests with license_security module."""
    
    def test_get_license_secret_key(self):
        """Test that get_license_secret_key returns valid key."""
        from app.core.license_security import get_license_secret_key
        
        key = get_license_secret_key()
        
        # Should be bytes
        assert isinstance(key, bytes)
        
        # Should be correct length for Fernet key (44 bytes Base64)
        assert len(key) == 44
        
        # Should start with expected prefix (our known key)
        assert key.startswith(b'8kHs')
        
    def test_license_key_encryption_works(self):
        """Test that license decryption actually works with obfuscated key."""
        from cryptography.fernet import Fernet
        import json
        from app.core.license_security import get_license_secret_key
        
        # Get the obfuscated key
        key = get_license_secret_key()
        cipher = Fernet(key)
        
        # Create test license data
        test_license = {
            "Hardware ID": "TEST123",
            "Scadenza Licenza": "31/12/2025",
            "Cliente": "Test Customer"
        }
        
        # Encrypt
        encrypted = cipher.encrypt(json.dumps(test_license).encode('utf-8'))
        
        # Decrypt
        decrypted = cipher.decrypt(encrypted)
        recovered = json.loads(decrypted.decode('utf-8'))
        
        assert recovered == test_license
        
    def test_key_consistency(self):
        """Test that key is consistent across multiple calls."""
        from app.core.license_security import get_license_secret_key
        
        key1 = get_license_secret_key()
        key2 = get_license_secret_key()
        key3 = get_license_secret_key()
        
        assert key1 == key2 == key3


class TestSecurityProperties:
    """Tests for security properties of obfuscation."""
    
    def test_obfuscated_looks_random(self):
        """Test that obfuscated output appears random (not recognizable pattern)."""
        secrets = [
            "API_KEY_12345",
            "API_KEY_12346",  # Very similar input
        ]
        
        obfuscated = [obfuscate_string(s) for s in secrets]
        
        # Similar inputs should produce different-looking outputs
        # (due to XOR, single char difference propagates)
        assert obfuscated[0] != obfuscated[1]
        
    def test_no_plaintext_fragments_in_binary(self):
        """Test that no recognizable plaintext fragments remain."""
        sensitive_strings = [
            "ghp_",  # GitHub token prefix
            "AIzaSy",  # Google API key prefix
            "sk-",  # OpenAI key prefix
            "8kHs_",  # Our Fernet key prefix
        ]
        
        for prefix in sensitive_strings:
            test_string = prefix + "x" * 30
            obfuscated = obfuscate_string(test_string)
            
            # The prefix should not appear in obfuscated output
            assert prefix not in obfuscated, f"Prefix '{prefix}' found in obfuscated output"

