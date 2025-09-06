# video_creation_cli/tests/test_consolidation.py

import unittest
import os
import json
import sys

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import config

class TestDataConsolidation(unittest.TestCase):

    def setUp(self):
        """Set up a temporary output directory for tests."""
        self.test_output_dir = "test_output"
        os.makedirs(self.test_output_dir, exist_ok=True)

    def tearDown(self):
        """Clean up the temporary output directory and files after tests."""
        temp_file = os.path.join(self.test_output_dir, config.CONSOLIDATED_JSON_FILE)
        if os.path.exists(temp_file):
            os.remove(temp_file)
        if os.path.exists(self.test_output_dir):
            os.rmdir(self.test_output_dir)

    def test_save_and_load_consolidated_json(self):
        """
        Tests that a consolidated analysis dictionary can be saved to and loaded from a JSON file.
        """
        # 1. Create sample consolidated data
        sample_data = {
            "S1": {
                "scene_text": "This is scene 1.",
                "analysis": {
                    "sentiment": {"scores": {"compound": 0.5}, "dominant_emotion": "Positive"}
                }
            },
            "S2": {
                "scene_text": "This is scene 2.",
                "analysis": {
                    "sentiment": {"scores": {"compound": -0.5}, "dominant_emotion": "Negative"}
                }
            }
        }

        # 2. Define the file path and save the data
        file_path = os.path.join(self.test_output_dir, config.CONSOLIDATED_JSON_FILE)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=4)

        # 3. Assert that the file was created
        self.assertTrue(os.path.exists(file_path))

        # 4. Read the file back
        with open(file_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)

        # 5. Assert that the loaded data is identical to the original data
        self.assertEqual(sample_data, loaded_data)

if __name__ == '__main__':
    unittest.main()
