# src/assets/audio.py

from gtts import gTTS
from mutagen.mp3 import MP3
import os

def generate_audio(scene_key, scene_text, audio_dir):
    """
    Generates a text-to-speech audio file for the given scene text.
    Returns the file path and duration of the audio file.
    """
    audio_filename = f"{scene_key}.mp3"
    audio_filepath = os.path.join(audio_dir, audio_filename)

    try:
        tts = gTTS(text=scene_text, lang='en')
        tts.save(audio_filepath)

        audio = MP3(audio_filepath)
        duration = audio.info.length

        return audio_filepath, duration
    except Exception as e:
        print(f"Error generating audio for scene {scene_key}: {e}")
        return None, None
