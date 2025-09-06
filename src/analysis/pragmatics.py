# src/analysis/pragmatics.py

def analyze_pragmatics(text, nlp):
    """
    Performs pragmatic analysis on the text to identify sentence types and conjunctions.
    """
    doc = nlp(text)
    sentence_types = {}
    conjunctions = []

    for sent in doc.sents:
        if sent.text.strip().endswith('.'):
            sentence_types['declarative'] = sentence_types.get('declarative', 0) + 1
        elif sent.text.strip().endswith('?'):
            sentence_types['interrogative'] = sentence_types.get('interrogative', 0) + 1
        elif sent.text.strip().endswith('!'):
            sentence_types['exclamatory'] = sentence_types.get('exclamatory', 0) + 1

    for token in doc:
        if token.pos_ == 'CCONJ' or token.pos_ == 'SCONJ':
            conjunctions.append(token.text)
            
    return {
        'sentence_types': sentence_types,
        'conjunctions': conjunctions
    }
