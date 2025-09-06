# video_creation_cli/src/config.py

import os

# API Keys
PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")  # API key is loaded from environment variable
LETTER = "loveletter.txt"
# File and Directory Names
OUTPUT_DIR = "output"
CONSOLIDATED_JSON_FILE = "consolidated_analysis_results.json"
QUERY_LOG_FILE = "QueryLog.json"
AUDIO_DIR = "audio"
VIDEO_CLIPS_DIR = "video_clips"
ADJUSTED_CLIPS_DIR = "adjusted_video_clips"

# NLP Model Names
SPACY_MODEL = "en_core_web_sm"
EMOTION_MODEL = "cardiffnlp/twitter-roberta-base-emotion"

# Pixabay Settings
PIXABAY_PER_PAGE = 200
PIXABAY_ORDER = "latest"

# Script Settings
TEXT_EXTRACTION_WORD_COUNT = 10000
SCENE_JSON_FILE = "scenes.json"
MAX_SENTENCES_PER_SCENE = 3

# Overall Settings Keywords
SETTINGS_KEYWORDS = {
    'locations': ['forest', 'clearing', 'portal', 'tree', 'distance', 'city', 'lights'],
    'atmosphere': ['mysterious', 'tall', 'thick', 'fog', 'strange', 'scared', 'friendly', 'cautious', 'long', 'challenging', 'changed', 'golden', 'glow', 'deep', 'peace', 'hopeful', 'heavy', 'sad', 'bittersweet', 'beautiful']
}
