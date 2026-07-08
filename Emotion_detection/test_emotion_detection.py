import unittest
from unittest.mock import patch

from EmotionDetection import emotion_detector
import EmotionDetection.emotion_detection as emotion_module


class TestEmotionDetection(unittest.TestCase):
    def test_blank_input_returns_400_and_none_values(self):
        result, status_code = emotion_detector("   ")
        self.assertEqual(status_code, 400)
        self.assertIsNone(result["anger"])
        self.assertIsNone(result["disgust"])
        self.assertIsNone(result["fear"])
        self.assertIsNone(result["joy"])
        self.assertIsNone(result["sadness"])
        self.assertIsNone(result["dominant_emotion"])

    def test_emotion_detector_formats_output_and_sets_dominant_emotion(self):
        raw = {
            "anger": 0.1,
            "disgust": 0.2,
            "fear": 0.3,
            "joy": 0.4,
            "sadness": 0.05,
        }
        with patch.object(emotion_module, "_predict_emotions_watson", return_value=raw):
            result, status_code = emotion_detector("I am happy today")

        self.assertEqual(status_code, 200)
        self.assertAlmostEqual(result["anger"], 0.1)
        self.assertAlmostEqual(result["disgust"], 0.2)
        self.assertAlmostEqual(result["fear"], 0.3)
        self.assertAlmostEqual(result["joy"], 0.4)
        self.assertAlmostEqual(result["sadness"], 0.05)
        self.assertEqual(result["dominant_emotion"], "joy")

    def test_emotion_detector_does_not_crash_when_raw_structure_is_unparseable(self):
        with patch.object(emotion_module, "_predict_emotions_watson", return_value={"unexpected": 1}):
            result, status_code = emotion_detector("Unparseable raw response")

        self.assertEqual(status_code, 200)
        self.assertIn(result["dominant_emotion"], emotion_module.EMOTIONS)
        self.assertTrue(all(isinstance(result[e], float) for e in emotion_module.EMOTIONS))


if __name__ == "__main__":
    unittest.main()

