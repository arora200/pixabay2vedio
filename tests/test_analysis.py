# video_creation_cli/tests/test_analysis.py

import unittest
import spacy
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from analysis.entities import extract_text, check_spelling, identify_entities, segment_text_into_scenes
from analysis.sentiment import analyze_sentiment
from analysis.emotion import analyze_emotion
from analysis.pragmatics import analyze_pragmatics
from config import SPACY_MODEL, EMOTION_MODEL

class TestAnalysis(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Load the spaCy model once for all tests."""
        try:
            cls.nlp = spacy.load(SPACY_MODEL)
        except OSError:
            spacy.cli.download(SPACY_MODEL)
            cls.nlp = spacy.load(SPACY_MODEL)

    def test_extract_text(self):
        script = "word1 word2 word3 word4 word5"
        extracted = extract_text(script, 3)
        self.assertEqual(extracted, "word1 word2 word3")

    def test_check_spelling(self):
        text = "This is a test with a mispelled word."
        misspelled = check_spelling(text)
        self.assertIn("mispelled", misspelled)

    def test_identify_entities(self):
        text = "The quick brown fox jumps over the lazy dog."
        entities = identify_entities(text, self.nlp)
        self.assertIn("fox", entities['nouns'])
        self.assertIn("jumps", entities['verbs'])
        # This test is designed to fail to show the test suite is working
        # self.assertIn("quickly", entities['adverbs']) 

    def test_segment_text_into_scenes(self):
        text = "This is an intro. Scene 1: The first scene. Scene 2: The second scene."
        scenes = segment_text_into_scenes(text)
        self.assertIn("S0", scenes)
        self.assertEqual(scenes['S0'], "This is an intro.")
        self.assertIn("S1", scenes)
        self.assertEqual(scenes['S1'], "The first scene.")
        self.assertIn("S2", scenes)
        self.assertEqual(scenes['S2'], "The second scene.")
        self.assertEqual(len(scenes), 3) # S0, S1, S2

    def test_analyze_sentiment(self):
        text = "This is a wonderful and happy sentence."
        sentiment = analyze_sentiment(text)
        self.assertEqual(sentiment['dominant_emotion'], 'Positive')
        self.assertGreater(sentiment['scores']['compound'], 0.5)

    def test_analyze_emotion(self):
        text = "I am so happy and excited today."
        emotion = analyze_emotion(text, EMOTION_MODEL)
        # The model is likely to return 'joy' or 'love'
        self.assertIn(emotion.get('label'), ['joy', 'love', 'optimism'])

    def test_analyze_pragmatics(self):
        text = "This is a statement. Is this a question? This is an exclamation!"
        pragmatics = analyze_pragmatics(text, self.nlp)
        self.assertEqual(pragmatics['sentence_types']['declarative'], 1)
        self.assertEqual(pragmatics['sentence_types']['interrogative'], 1)
        self.assertEqual(pragmatics['sentence_types']['exclamatory'], 1)

if __name__ == '__main__':
    unittest.main()
