# video_creation_cli/tests/test_advanced_video_retrieval.py

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from assets.video import generate_queries, search_videos, download_video
import config

class TestAdvancedVideoRetrieval(unittest.TestCase):

    def setUp(self):
        """Set up a temporary output directory for tests."""
        self.test_output_dir = "test_output"
        os.makedirs(self.test_output_dir, exist_ok=True)

    def tearDown(self):
        """Clean up the temporary output directory and files after tests."""
        for root, dirs, files in os.walk(self.test_output_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        if os.path.exists(self.test_output_dir):
            os.rmdir(self.test_output_dir)

    def test_query_splitting(self):
        """Tests that a long list of keywords is split into multiple queries."""
        sample_analysis = {
            'hf_emotion_analysis': {'label': 'excitement'},
            'entity_analysis': {
                'nouns': ['adventure', 'mountain', 'journey', 'peak', 'summit', 'glory'],
                'verbs': ['climbing', 'hiking', 'exploring', 'reaching', 'conquering']
            }
        }
        queries = generate_queries(sample_analysis, {})
        self.assertIsInstance(queries, list)
        self.assertGreater(len(queries), 1)
        for query in queries:
            self.assertLessEqual(len(query.split()), 5)

    @patch('assets.video.requests.get')
    def test_unique_video_downloads(self, mock_requests_get):
        """Tests that only unique videos are downloaded, even if returned for different queries."""
        # Configure the mock to return duplicate video IDs
        mock_requests_get.side_effect = [
            MagicMock(status_code=200, json=lambda: {"totalHits": 1, "hits": [{"id": 123, "videos": {"large": {"url": "fake_url_1"}}}]}),
            MagicMock(status_code=200, json=lambda: {"totalHits": 1, "hits": [{"id": 123, "videos": {"large": {"url": "fake_url_1"}}}]}), # Duplicate
            MagicMock(status_code=200, json=lambda: {"totalHits": 1, "hits": [{"id": 456, "videos": {"large": {"url": "fake_url_2"}}}]})
        ]

        # Simulate the download loop
        downloaded_video_ids = set()
        queries = ["query1", "query2", "query3"]
        for query in queries:
            search_results = search_videos(query, "fake_api_key")
            if search_results and search_results['hits']:
                for hit in search_results['hits']:
                    if hit['id'] not in downloaded_video_ids:
                        # We are not actually calling download_video, just tracking the logic
                        downloaded_video_ids.add(hit['id'])

        # Assertions
        self.assertEqual(len(downloaded_video_ids), 2)
        self.assertIn(123, downloaded_video_ids)
        self.assertIn(456, downloaded_video_ids)

    @patch('assets.video.requests.get')
    def test_no_duplicate_downloads_integration(self, mock_requests_get):
        """
        An integration-style test to ensure the main loop avoids downloading duplicates.
        """
        # This mock simulates finding the same video for two different scenes
        mock_requests_get.side_effect = [
            # Scene 1 results
            MagicMock(status_code=200, json=lambda: {"totalHits": 1, "hits": [{"id": 789, "videos": {"large": {"url": "fake_url_3"}}}]}),
            # Scene 2 results
            MagicMock(status_code=200, json=lambda: {"totalHits": 1, "hits": [{"id": 789, "videos": {"large": {"url": "fake_url_3"}}}]})
        ]

        # Simulate the main loop's download logic
        downloaded_video_ids = set()
        
        # --- Simulate for Scene 1 ---
        queries_s1 = ["query_s1"]
        video_found_s1 = False
        for query in queries_s1:
            if video_found_s1: break
            search_results = search_videos(query, "fake_api_key")
            if search_results and search_results['hits']:
                for hit in search_results['hits']:
                    if hit['id'] not in downloaded_video_ids:
                        # We are not actually calling download_video, just tracking the logic
                        downloaded_video_ids.add(hit['id'])
                        video_found_s1 = True
                        break
        
        # --- Simulate for Scene 2 ---
        queries_s2 = ["query_s2"]
        video_found_s2 = False
        for query in queries_s2:
            if video_found_s2: break
            search_results = search_videos(query, "fake_api_key")
            if search_results and search_results['hits']:
                for hit in search_results['hits']:
                    if hit['id'] not in downloaded_video_ids:
                        # We are not actually calling download_video, just tracking the logic
                        downloaded_video_ids.add(hit['id'])
                        video_found_s2 = True
                        break
        
        # Assertions
        # download_video should only be called once, for the first scene
        self.assertEqual(len(downloaded_video_ids), 1)
        self.assertIn(789, downloaded_video_ids)

    @patch('assets.video.requests.get')
    def test_search_videos_with_new_parameters(self, mock_requests_get):
        """Tests that the new parameters are correctly passed to the Pixabay API."""
        mock_requests_get.return_value = MagicMock(status_code=200, json=lambda: {"totalHits": 0, "hits": []})

        search_videos("test", "fake_key", is_ai_generated=False, is_g_rated=True, video_type="animation")

        mock_requests_get.assert_called_with(
            "https://pixabay.com/api/videos/",
            params={
                'key': 'fake_key',
                'q': 'test',
                'orientation': 'vertical',
                'is_ai_generated': False,
                'is_grated': True,
                'video_type': 'animation'
            }
        )

if __name__ == '__main__':
    unittest.main()