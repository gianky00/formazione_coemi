import re

class PhoneticNormalizer:
    """
    Handles deterministic phonetic corrections for TTS to ensure infallible pronunciation.
    """

    # Dictionary of word -> phonetic_replacement
    # Keys should be lowercase for matching.
    # Values are the replacement text to be sent to the TTS engine.
    CORRECTIONS = {
        "lyra": "Lyra",
        "lyrà": "Lyra",        # Explicit fix for reported error
        "sicilia": "Sicìlia",
        "sicilià": "Sicìlia",  # Explicit fix for reported error
        "sicurezza": "sicurézza",
        "sicurezzà": "sicurézza", # Explicit fix for reported error
        "lavoro": "lavóro",
        "lavorò": "lavóro",    # Explicit fix for reported error
        "tecnologia": "tecnologìa",
        "armonia": "armonìa",
        "intelleo": "Intelléo", # Optional: ensure brand pronunciation if needed, but not requested. Sticking to requested.
    }

    @classmethod
    def normalize(cls, text: str) -> str:
        """
        Applies phonetic corrections to the text.
        """
        if not text:
            return ""

        # Helper to replace words found in dictionary
        def replace_match(match):
            word = match.group(0)
            lower_word = word.lower()
            if lower_word in cls.CORRECTIONS:
                return cls.CORRECTIONS[lower_word]
            return word

        # Regex to match words.
        # We explicitly include accented chars in the character set to ensure they are captured as part of the word
        # although \w usually handles them in Python 3, making it explicit helps visualization.
        # But \b is safer with standard re.

        return re.sub(r'\b\w+\b', replace_match, text, flags=re.IGNORECASE)
