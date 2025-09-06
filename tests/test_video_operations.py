# video_creation_cli/tests/test_video_operations.py

import unittest
from unittest.mock import patch, MagicMock
import os
import sys
import moviepy.editor as mp

# Add the src directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from assets.video import download_video, adjust_video_duration, create_final_video
import config

class TestVideoOperations(unittest.TestCase):

    def setUp(self):
        """Set up a temporary output directory and dummy files for tests."""
        self.test_output_dir = "test_output"
        os.makedirs(self.test_output_dir, exist_ok=True)
        self.dummy_video_path = "dummy_video.mp4"
        self.dummy_audio_path = "dummy_audio.mp3"

    def tearDown(self):
        """Clean up the temporary output directory and files after tests."""
        # This is a bit of a hack to release file handles on Windows
        import gc
        gc.collect()
        
        for root, dirs, files in os.walk(self.test_output_dir, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except PermissionError:
                    print(f"Could not remove {name} on teardown.")
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        if os.path.exists(self.test_output_dir):
            os.rmdir(self.test_output_dir)

    @patch('assets.video.requests.get')
    def test_download_video(self, mock_get):
        """Tests the video download function."""
        mock_response = MagicMock()
        with open(self.dummy_video_path, 'rb') as f:
            mock_response.iter_content.return_value = [f.read()]
        mock_get.return_value = mock_response

        save_path = os.path.join(self.test_output_dir, "test_video.mp4")
        success = download_video("http://fakeurl.com/video.mp4", save_path)

        self.assertTrue(success)
        self.assertTrue(os.path.exists(save_path))

    def test_adjust_duration_trim(self):
        """Tests trimming a video to a shorter duration."""
        output_path = os.path.join(self.test_output_dir, "trimmed_video.mp4")
        target_duration = 3.0
        
        success = adjust_video_duration(self.dummy_video_path, output_path, target_duration)
        self.assertTrue(success)
        
        trimmed_clip = mp.VideoFileClip(output_path)
        self.assertAlmostEqual(trimmed_clip.duration, target_duration, delta=0.1)
        trimmed_clip.close()

    def test_adjust_duration_loop(self):
        """Tests looping a video to a longer duration."""
        output_path = os.path.join(self.test_output_dir, "looped_video.mp4")
        target_duration = 7.0

        success = adjust_video_duration(self.dummy_video_path, output_path, target_duration)
        self.assertTrue(success)
        
        looped_clip = mp.VideoFileClip(output_path)
        self.assertAlmostEqual(looped_clip.duration, target_duration, delta=0.1)
        looped_clip.close()

    def test_resolution_conformance(self):
        """Tests if the video resolution has a 9:16 aspect ratio."""
        clip = mp.VideoFileClip(self.dummy_video_path)
        self.assertEqual(clip.size, [1080, 1920])
        self.assertAlmostEqual(clip.aspect_ratio, 9/16, delta=0.01)
        clip.close()

    def test_create_final_video(self):
        """Tests the creation of the final concatenated video."""
        # Create some dummy adjusted clips for testing
        adjusted_clips_dir = os.path.join(self.test_output_dir, config.ADJUSTED_CLIPS_DIR)
        os.makedirs(adjusted_clips_dir, exist_ok=True)
        
        clip1_path = os.path.join(adjusted_clips_dir, "S1_adjusted.mp4")
        clip2_path = os.path.join(adjusted_clips_dir, "S2_adjusted.mp4")
        
        adjust_video_duration(self.dummy_video_path, clip1_path, 2.0)
        adjust_video_duration(self.dummy_video_path, clip2_path, 3.0)

        consolidated_data = {
            "S1": {
                "adjusted_video_info": {"path": clip1_path},
                "audio_info": {"filename": self.dummy_audio_path, "duration": 10.0}
            },
            "S2": {
                "adjusted_video_info": {"path": clip2_path},
                "audio_info": {"filename": self.dummy_audio_path, "duration": 10.0}
            }
        }

        final_video_path, total_duration = create_final_video(consolidated_data, self.test_output_dir)
        
        self.assertIsNotNone(final_video_path)
        self.assertTrue(os.path.exists(final_video_path))
        
        final_clip = mp.VideoFileClip(final_video_path)
        # The total duration should be the sum of the audio durations
        self.assertAlmostEqual(final_clip.duration, 20.0, delta=0.1)
        final_clip.close()

if __name__ == '__main__':
    unittest.main()
