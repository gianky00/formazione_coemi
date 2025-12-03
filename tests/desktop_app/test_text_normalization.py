import sys
import unittest
from unittest.mock import MagicMock

# Mock PyQt6 before importing desktop_app.utils
sys.modules["PyQt6"] = MagicMock()
sys.modules["PyQt6.QtGui"] = MagicMock()
sys.modules["PyQt6.QtCore"] = MagicMock()

# Now import the utility
from desktop_app.utils import clean_text_for_display

class TestTextNormalization(unittest.TestCase):
    def test_phonetic_stress_removal(self):
        self.assertEqual(clean_text_for_display("Sóno prónta"), "Sono pronta")
        self.assertEqual(clean_text_for_display("càsa"), "casa")
        self.assertEqual(clean_text_for_display("pèsca"), "pesca")
        self.assertEqual(clean_text_for_display("bótte"), "botte")

    def test_end_of_word_preservation(self):
        self.assertEqual(clean_text_for_display("città"), "città")
        self.assertEqual(clean_text_for_display("perché"), "perché")
        self.assertEqual(clean_text_for_display("però"), "però")
        self.assertEqual(clean_text_for_display("metrò"), "metrò")
        self.assertEqual(clean_text_for_display("così"), "così")
        self.assertEqual(clean_text_for_display("più"), "più")

    def test_proparoxytone_handling(self):
        # New test case for the requested feature
        self.assertEqual(clean_text_for_display("assìsterti"), "assisterti")
        self.assertEqual(clean_text_for_display("màcchina"), "macchina")
        self.assertEqual(clean_text_for_display("tàvolo"), "tavolo")
        self.assertEqual(clean_text_for_display("dìmmelo"), "dimmelo")

    def test_punctuation_interaction(self):
        self.assertEqual(clean_text_for_display("Sono prónta."), "Sono pronta.")
        self.assertEqual(clean_text_for_display("È così?"), "È così?")
        self.assertEqual(clean_text_for_display("È vero"), "È vero")

    def test_markdown_interaction(self):
        self.assertEqual(clean_text_for_display("**Sóno**"), "**Sono**")
        self.assertEqual(clean_text_for_display("*però*"), "*però*")
        self.assertEqual(clean_text_for_display("**città**"), "**città**")
        self.assertEqual(clean_text_for_display("[pèsca](link)"), "[pesca](link)")

        # New edge case tests for underscores
        self.assertEqual(clean_text_for_display("_città_"), "_città_")
        self.assertEqual(clean_text_for_display("_pèsca_"), "_pesca_")
        self.assertEqual(clean_text_for_display("word_connected"), "word_connected")

    def test_specific_replacements(self):
        self.assertEqual(clean_text_for_display("á"), "a")
        self.assertEqual(clean_text_for_display("í"), "i")
        self.assertEqual(clean_text_for_display("ú"), "u")

if __name__ == '__main__':
    unittest.main()
