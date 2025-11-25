import base64

OBFUSCATION_PREFIX = "obf:"

def obfuscate_string(s: str) -> str:
    """
    Reverses a string, encodes it in Base64, and adds a prefix.
    Returns an empty string if the input is empty.
    """
    if not s:
        return ""
    reversed_string = s[::-1]
    encoded_bytes = base64.b64encode(reversed_string.encode('utf-8'))
    return f"{OBFUSCATION_PREFIX}{encoded_bytes.decode('utf-8')}"

def reveal_string(obfuscated_s: str) -> str:
    """
    Decodes a prefixed Base64 string and reverses it to restore the original.
    Returns the input string directly if it's not prefixed, empty, or invalid.
    """
    if not obfuscated_s or not obfuscated_s.startswith(OBFUSCATION_PREFIX):
        return obfuscated_s

    try:
        to_decode = obfuscated_s[len(OBFUSCATION_PREFIX):]
        # Pad the string with '=' if its length is not a multiple of 4
        padded_to_decode = to_decode + '=' * (-len(to_decode) % 4)
        decoded_bytes = base64.b64decode(padded_to_decode.encode('utf-8'))
        reversed_string = decoded_bytes.decode('utf-8')
        return reversed_string[::-1]
    except (base64.binascii.Error, UnicodeDecodeError):
        # If decoding fails, it might be a normal string that coincidentally
        # started with the prefix. Return it as is.
        return obfuscated_s
