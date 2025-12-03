import pytest
from desktop_app.chat.phonetic_utils import PhoneticNormalizer

class TestPhoneticNormalizer:

    def test_normalize_basic(self):
        text = "La sicurezza sul lavoro è importante."
        normalized = PhoneticNormalizer.normalize(text)
        assert "sicurézza" in normalized
        assert "lavóro" in normalized
        assert normalized == "La sicurézza sul lavóro è importante."

    def test_normalize_errors(self):
        """Tests specific fixes for the errors reported by the user."""
        text = "Sono Lyrà, nata in Sicilià. Gestisco la sicurezzà sul lavorò."
        normalized = PhoneticNormalizer.normalize(text)

        assert "Lyra" in normalized
        assert "Lyrà" not in normalized

        assert "Sicìlia" in normalized
        assert "Sicilià" not in normalized

        assert "sicurézza" in normalized
        assert "sicurezzà" not in normalized

        assert "lavóro" in normalized
        assert "lavorò" not in normalized

        expected = "Sono Lyra, nata in Sicìlia. Gestisco la sicurézza sul lavóro."
        assert normalized == expected

    def test_normalize_mixed_case(self):
        text = "SICUREZZA e Lavoro."
        normalized = PhoneticNormalizer.normalize(text)
        # Dictionary values are currently Title Case or specific case.
        # The current implementation returns the dictionary value exactly.
        # "sicurézza" (lowercase) and "lavóro" (lowercase).
        # "SICUREZZA" -> "sicurezza" (key) -> "sicurézza" (value).
        # If we wanted to preserve case (SICURÉZZA), we'd need more logic.
        # But for TTS, case usually doesn't matter for pronunciation, only accents.
        # So "sicurézza" is fine even if original was CAPS.
        assert "sicurézza" in normalized
        assert "lavóro" in normalized

    def test_no_change(self):
        text = "Ciao come stai?"
        normalized = PhoneticNormalizer.normalize(text)
        assert normalized == text
