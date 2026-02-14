import sys

from app.utils.security import obfuscate_string, reveal_string


def main():
    print("Intelleo Key Obfuscation Utility")
    print("--------------------------------")

    if len(sys.argv) > 1:
        raw_key = sys.argv[1]
    else:
        raw_key = input("Enter the raw API Key to obfuscate: ").strip()

    if not raw_key:
        print("Error: No key provided.")
        return

    obfuscated = obfuscate_string(raw_key)
    print(f"\nObfuscated Key: {obfuscated}")

    # Verification
    revealed = reveal_string(obfuscated)
    if revealed == raw_key:
        print("Verification: SUCCESS (Decoded matches original)")
    else:
        print("Verification: FAILED")


if __name__ == "__main__":
    main()
