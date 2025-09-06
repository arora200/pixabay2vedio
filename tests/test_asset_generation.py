# video_creation_cli/tests/test_asset_generation.py

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from assets.audio import generate_audio
from assets.video import generate_queries, search_videos, download_video
import config

class TestAssetGeneration(unittest.TestCase):

    def setUp(self):
        """Set up a temporary output directory for tests."""
        self.test_output_dir = "test_output"
        os.makedirs(self.test_output_dir, exist_ok=True)
        self.audio_dir = os.path.join(self.test_output_dir, config.AUDIO_DIR)
        os.makedirs(self.audio_dir, exist_ok=True)

    def tearDown(self):
        """Clean up the temporary output directory and files after tests."""
        # Clean up any files created in the test
        for root, dirs, files in os.walk(self.test_output_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(self.test_output_dir)

    @patch('assets.audio.gTTS')
    @patch('assets.audio.MP3')
    def test_generate_audio(self, mock_mp3, mock_gtts):
        """Tests the audio generation function using mocks."""
        # Configure the mocks
        mock_gtts_instance = MagicMock()
        mock_gtts.return_value = mock_gtts_instance
        
        mock_mp3_instance = MagicMock()
        mock_mp3_instance.info.length = 15.5
        mock_mp3.return_value = mock_mp3_instance

        # Call the function
        scene_key = "S1"
        scene_text = "This is a test scene."
        audio_filepath, duration = generate_audio(scene_key, scene_text, self.audio_dir)

        # Assertions
        expected_filepath = os.path.join(self.audio_dir, f"{scene_key}.mp3")
        self.assertEqual(audio_filepath, expected_filepath)
        self.assertEqual(duration, 15.5)
        mock_gtts_instance.save.assert_called_with(expected_filepath)

    def test_generate_queries(self):
        """Tests the query generation logic."""
        sample_analysis = {
            'hf_emotion_analysis': {'label': 'joy'},
            'entity_analysis': {'nouns': ['hero', 'forest'], 'verbs': ['walks']}
        }
        queries = generate_queries(sample_analysis, {})
        self.assertIsInstance(queries, list)
        self.assertGreater(len(queries), 0)
        self.assertIn("joy hero forest walks", queries)

    @patch('assets.video.requests.get')
    def test_search_videos(self, mock_get):
        """Tests the video search function using a mock API response."""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.json.return_value = {"totalHits": 1, "hits": [{"id": 123}]}
        mock_get.return_value = mock_response

        # Call the function
        results = search_videos("test query", "fake_api_key")

        # Assertions
        self.assertIsNotNone(results)
        self.assertEqual(results["totalHits"], 1)
        self.assertEqual(results["hits"][0]["id"], 123)

    @patch('assets.video.requests.get')
    def test_download_video(self, mock_get):
        """Tests the video download function."""
        # Configure the mock
        mock_response = MagicMock()
        mock_response.iter_content.return_value = [b'some', b'video', b'data']
        mock_get.return_value = mock_response

        # Call the function
        save_path = os.path.join(self.test_output_dir, "test_video.mp4")
        success = download_video("http://fakeurl.com/video.mp4", save_path)

        # Assertions
        self.assertTrue(success)
        self.assertTrue(os.path.exists(save_path))
        with open(save_path, 'rb') as f:
            content = f.read()
            self.assertEqual(content, b'somevideodata')

if __name__ == '__main__':
    unittest.main()
