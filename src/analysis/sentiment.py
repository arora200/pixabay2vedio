# src/analysis/sentiment.py

from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

def analyze_sentiment(text):
    """
    Analyzes the sentiment of the text using VADER.
    Downloads 'vader_lexicon' if not already present.
    """
    try:
        analyzer = SentimentIntensityAnalyzer()
    except LookupError:
        print("Downloading vader_lexicon for sentiment analysis...")
        nltk.download('vader_lexicon')
        analyzer = SentimentIntensityAnalyzer()
        
    scores = analyzer.polarity_scores(text)
    
    if scores['compound'] >= 0.05:
        dominant_emotion = 'Positive'
    elif scores['compound'] <= -0.05:
        dominant_emotion = 'Negative'
    else:
        dominant_emotion = 'Neutral'
        
    return {
        'scores': scores,
        'dominant_emotion': dominant_emotion
    }