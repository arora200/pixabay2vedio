# src/analysis/entities.py

from spellchecker import SpellChecker
import spacy
import config # Import config

def extract_text(script, word_count):
    """Extracts the first `word_count` words from the script."""
    words = script.split()
    extracted_words = words[:word_count]
    return ' '.join(extracted_words)

def check_spelling(text):
    """Checks the spelling of the text and returns a list of misspelled words."""
    spell = SpellChecker()
    misspelled = spell.unknown(text.split())
    return list(misspelled)

def identify_entities(text, nlp):
    """Identifies nouns, adverbs, and verbs in the text."""
    doc = nlp(text)
    entities = {
        'nouns': [],
        'adverbs': [],
        'verbs': []
    }
    for token in doc:
        if token.pos_ in ['NOUN', 'PROPN']:
            entities['nouns'].append(token.text)
        elif token.pos_ == 'ADV':
            entities['adverbs'].append(token.text)
        elif token.pos_ == 'VERB':
            entities['verbs'].append(token.text)
    return entities

# Renaming the old function for backup/reference
# def _old_segment_text_into_scenes(text):
#     """Segments the text into scenes, removing the 'Scene X: ' prefix from the narrative."""
#     segments = text.split("Scene ")
#     
#     # The first segment might be introductory text before "Scene 1"
#     # We'll keep it if it's not empty, but it won't be part of a numbered scene.
#     intro_text = ""
#     if segments[0].strip():
#         intro_text = segments[0].strip()
#         segments = segments[1:] # Process the rest as numbered scenes
#     else:
#         segments = segments[1:] # Skip empty first segment if no intro text
#
#     scenes_dict = {}
#     if intro_text:
#         scenes_dict["S0"] = intro_text # Assign intro text to S0
#
#     for segment in segments:
#         # Robustly find the scene number and separate the prefix from the narrative
#         parts = segment.split(":", 1) # Split only on the first colon
#         if len(parts) > 1:
#             header = parts[0].strip()
#             narrative_text = parts[1].strip()
#             
#             # Extract scene number from header (e.g., "1" from "1")
#             try:
#                 scene_number_str = header.split()[0].strip() # Assuming "1" from "1"
#                 scene_number = int(scene_number_str)
#                 scene_key = f"S{scene_number}"
#                 scenes_dict[scene_key] = narrative_text
#             except (ValueError, IndexError):
#                 print(f"Warning: Could not parse valid scene number from header: '{header}'. Skipping segment: '{segment}'")
#         else:
#             print(f"Warning: Segment does not contain a colon after 'Scene #': '{segment}'. Skipping.")
#             
#     return scenes_dict

def segment_text_into_scenes(text, nlp):
    """
    Segments the text into meaningful chunks (scenes) using spaCy,
    based on sentence and paragraph breaks.
    """
    doc = nlp(text)
    scenes_dict = {}
    current_scene_sentences = []
    scene_counter = 0

    # Group sentences into scenes
    for sent in doc.sents:
        current_scene_sentences.append(sent.text.strip())

        # Check for paragraph breaks (two consecutive newlines) or max sentences
        if (sent.text.endswith('\n\n') or
            len(current_scene_sentences) >= config.MAX_SENTENCES_PER_SCENE):
            
            if current_scene_sentences: # Ensure scene is not empty
                scene_counter += 1
                scene_key = f"S{scene_counter}"
                scenes_dict[scene_key] = " ".join(current_scene_sentences)
                current_scene_sentences = [] # Reset for next scene

    # Add any remaining sentences as the last scene
    if current_scene_sentences:
        scene_counter += 1
        scene_key = f"S{scene_counter}"
        scenes_dict[scene_key] = " ".join(current_scene_sentences)

    return scenes_dict


