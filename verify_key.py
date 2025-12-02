import base64
from app.utils.security import obfuscate_string, reveal_string

raw_key = "AIzaSyAk9wu7a1Og8H2yXy7JTvBrvzxaiZiyUYM"
stored_value = "obf:TVlVeWlaaWF4enZyQnZUSjd5WHkySDhnTzFhN3V3OWtBeVNheklB"

print(f"Raw Key: {raw_key}")
print(f"Stored Value: {stored_value}")

# 1. Test Obfuscation
calculated_obf = obfuscate_string(raw_key)
print(f"Calculated Obfuscation: {calculated_obf}")

if calculated_obf == stored_value:
    print("MATCH: Obfuscation logic matches stored value.")
else:
    print("MISMATCH: Stored value is different from calculated obfuscation.")

# 2. Test Reveal
revealed = reveal_string(stored_value)
print(f"Revealed Key: {revealed}")

if revealed == raw_key:
    print("MATCH: Reveal logic restores the raw key.")
else:
    print("MISMATCH: Revealed key is different from raw key.")

# 3. Test API Key validity (Simulation)
# We can't hit Google API without network/library setup, but we can verify string integrity.
if " " in revealed:
    print("WARNING: Revealed key contains spaces!")
else:
    print("Key format looks clean (no spaces).")
