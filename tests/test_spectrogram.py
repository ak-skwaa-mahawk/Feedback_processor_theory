import unittest
from unittest.mock import patch
from core.feedback_spectrogram import feedback_spectrogram, validate_passcode
from core.feedback_logger import log_metadata
import hashlib, json, math

class TestSpectrogram(unittest.TestCase):
    def setUp(self):
        self.conversation = [
            ("You", "Do you want me to give a ready-to-run Git commands script?"),
            ("Me", "Yo kin, you came in hot with this one! 🔥 Ready to push this live?")
        ]
        self.output_dir = "data/spectrograms/test"
        self.passcode = "XHT-421-FlameDrop"

    def test_validate_passcode_valid(self):
        self.assertTrue(validate_passcode(self.passcode))

    def test_validate_passcode_invalid(self):
        self.assertFalse(validate_passcode("wrong-passcode"))

    @patch("core.feedback_spectrogram.plt.savefig")
    @patch("core.feedback_spectrogram.os.makedirs")
    def test_feedback_spectrogram_valid(self, mock_makedirs, mock_savefig):
        result = feedback_spectrogram(self.conversation, self.passcode, self.output_dir)
        self.assertTrue(result.startswith(self.output_dir))
        self.assertTrue(result.endswith(".png"))

    def test_feedback_spectrogram_invalid(self):
        result = feedback_spectrogram(self.conversation, "wrong-passcode", self.output_dir)
        self.assertEqual(result, "Whisper’s listening. Invalid passcode—flame clearance denied.")

    @patch("core.feedback_logger.os.makedirs")
    def test_log_metadata_pi_hash(self, mock_makedirs):
        data = {"passcode": self.passcode}
        result = log_metadata("spectrogram_access", data, self.output_dir)
        with open(result) as f:
            log = json.load(f)
            expected_hash = hashlib.sha256((self.passcode + str(math.pi)).encode()).hexdigest()
            self.assertEqual(log["hashed_passcode"], expected_hash)
            self.assertEqual(log["pi_feedback_constant"], math.pi)

if __name__ == "__main__":
    unittest.main()