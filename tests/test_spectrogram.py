"""
Unit tests for Feedback Spectrogram module
Author: John Carroll / Two Mile Solutions LLC
"""
import unittest, os, json, shutil
from core.feedback_spectrogram import FeedbackSpectrogram, validate_passcode

class TestFeedbackSpectrogram(unittest.TestCase):
    def setUp(self):
        self.spec = FeedbackSpectrogram(output_dir="data/test_resonance")
        self.test_text = "Test resonance pattern with multiple words and tone!"
        self.passcode = "XHT-421-FlameDrop"

    def test_validate_passcode(self):
        self.assertTrue(validate_passcode(self.passcode))
        self.assertFalse(validate_passcode("wrong-passcode"))

    def test_analyze_valid(self):
        result = self.spec.analyze(self.test_text, self.passcode)
        token_count = len(self.test_text.split())
        self.assertEqual(len(result["low"]), token_count)
        self.assertEqual(len(result["mid"]), token_count)
        self.assertEqual(len(result["high"]), token_count)

    def test_analyze_invalid_passcode(self):
        with self.assertRaises(ValueError):
            self.spec.analyze(self.test_text, "wrong-passcode")

    def test_log_creates_files(self):
        log_path = self.spec.log(self.test_text, self.passcode, meta={"test": True})
        self.assertTrue(os.path.exists(log_path))
        with open(log_path) as f:
            data = json.load(f)
            self.assertIn("pi_feedback_constant", data)

    def tearDown(self):
        if os.path.exists("data/test_resonance"):
            shutil.rmtree("data/test_resonance")

if __name__ == "__main__":
    unittest.main()