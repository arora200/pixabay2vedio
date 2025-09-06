# src/analysis/emotion.py

from transformers import pipeline

emotion_analyzer = None

def analyze_emotion(text, model_name):
    """
    Analyzes the emotion of the text using a Hugging Face transformer model.
    """
    global emotion_analyzer
    try:
        if emotion_analyzer is None:
            emotion_analyzer = pipeline("sentiment-analysis", model=model_name, truncation=True, max_length=512)
        emotion_scores = emotion_analyzer(text)[0]
        return emotion_scores
    except Exception as e:
        print(f"Error during emotion analysis: {e}")
        return {}
