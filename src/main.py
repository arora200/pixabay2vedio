# src/main.py

import argparse
import os
import json
import spacy
from datetime import datetime
import time

from utils.file_helpers import read_text_file
from analysis.entities import extract_text, check_spelling, identify_entities, segment_text_into_scenes
from analysis.sentiment import analyze_sentiment
from analysis.emotion import analyze_emotion
from analysis.pragmatics import analyze_pragmatics
from assets.audio import generate_audio
from assets.video import generate_queries, search_videos, download_video, adjust_video_duration, create_final_video, standardize_video_clip
import config

def main():
    parser = argparse.ArgumentParser(description="A CLI tool to process a video script and generate assets.")
    parser.add_argument("--script_path", required=True, help="The path to the input text file containing the script.")
    parser.add_argument("--output_dir", default=config.OUTPUT_DIR, help="The path to the directory where the final assets will be saved.")
    parser.add_argument("--api_key", default=config.PIXABAY_API_KEY, help="The Pixabay API key. Can also be set via the PIXABAY_API_KEY environment variable.")
    parser.add_argument("--skip_downloads", action="store_true", help="A flag to run the analysis without downloading videos.")
    
    # New arguments for Pixabay API filtering
    parser.add_argument("--exclude_ai", action="store_true", help="If set, excludes AI-generated content (note: Pixabay API does not directly support this filter).")
    parser.add_argument("--safesearch", action="store_true", help="If set, enables Pixabay's safesearch (equivalent to G-rated).")
    parser.add_argument("--video_type", default="film", help="The type of video to search for (e.g., 'film', 'animation').")
    # New arguments for video diversity
    parser.add_argument("--per_page", type=int, default=config.PIXABAY_PER_PAGE, help="Number of results per page from Pixabay.")
    parser.add_argument("--order", default=config.PIXABAY_ORDER, help="Order of results from Pixabay (popular, latest).")
    
    args = parser.parse_args()

    if not args.api_key:
        print("Error: Pixabay API key not found. Please set the PIXABAY_API_KEY environment variable or provide it using the --api_key argument.")
        return

    # --- 1. Initialization ---
    print("--- Phase 1: Initialization ---")
    os.makedirs(args.output_dir, exist_ok=True)
    
    script_text = read_text_file(args.script_path)
    if not script_text:
        return

    try:
        nlp = spacy.load(config.SPACY_MODEL)
    except OSError:
        print(f"Downloading spaCy model: {config.SPACY_MODEL}")
        spacy.cli.download(config.SPACY_MODEL)
        nlp = spacy.load(config.SPACY_MODEL)

    # --- 2. Script Analysis ---
    print("\n--- Phase 2: Script Analysis ---")
    # Removed extracted_text as it's no longer needed for segmentation
    # extracted_text = extract_text(script_text, config.TEXT_EXTRACTION_WORD_COUNT)
    
    # Pass nlp to the new segment_text_into_scenes function
    scenes_dict = segment_text_into_scenes(script_text, nlp)

    # Save scenes_dict to scene.json
    scenes_json_path = os.path.join(args.output_dir, config.SCENE_JSON_FILE)
    with open(scenes_json_path, 'w', encoding='utf-8') as f:
        json.dump(scenes_dict, f, indent=4)
    print(f"Scenes saved to: {scenes_json_path}")
    
    consolidated_analysis = {}
    for scene_key, scene_text in scenes_dict.items():
        print(f"Analyzing scene: {scene_key}")
        consolidated_analysis[scene_key] = {
            'scene_text': scene_text,
            'analysis': {
                'spell_check': check_spelling(scene_text),
                'sentiment': analyze_sentiment(scene_text),
                'emotion': analyze_emotion(scene_text, config.EMOTION_MODEL),
                'pragmatics': analyze_pragmatics(scene_text, nlp),
                'entities': identify_entities(scene_text, nlp)
            }
        }

    # --- 3. Asset Generation & Retrieval ---
    print("\n--- Phase 3: Asset Generation & Retrieval ---")
    audio_dir = os.path.join(args.output_dir, config.AUDIO_DIR)
    os.makedirs(audio_dir, exist_ok=True)
    
    for scene_key, scene_data in consolidated_analysis.items():
        print(f"Generating audio for scene: {scene_key}")
        audio_filepath, duration = generate_audio(scene_key, scene_data['scene_text'], audio_dir)
        consolidated_analysis[scene_key]['audio_info'] = {
            'filename': audio_filepath,
            'duration': duration
        }

    if not args.skip_downloads:
        video_clips_dir = os.path.join(args.output_dir, config.VIDEO_CLIPS_DIR)
        os.makedirs(video_clips_dir, exist_ok=True)
        query_log = []
        downloaded_video_ids = set() # Set to track downloaded video IDs
        
        overall_settings = {
            'locations': [],
            'atmosphere': []
        }
        # Use script_text for overall settings, not extracted_text
        doc = nlp(script_text)
        for token in doc:
            if token.pos_ in ['NOUN', 'PROPN'] and token.text.lower() in config.SETTINGS_KEYWORDS['locations']:
                if token.text not in overall_settings['locations']:
                    overall_settings['locations'].append(token.text)
            if token.text.lower() in config.SETTINGS_KEYWORDS['atmosphere']:
                if token.text not in overall_settings['atmosphere']:
                    overall_settings['atmosphere'].append(token.text)

        for scene_key, scene_data in consolidated_analysis.items():
            print(f"Retrieving video for scene: {scene_key}")
            queries = generate_queries(scene_data['analysis'], overall_settings)
            consolidated_analysis[scene_key]['generated_queries'] = queries
            
            video_found = False
            for query in queries:
                if video_found: break
                search_results = search_videos(
                    query,
                    args.api_key,
                    is_g_rated=args.safesearch,
                    video_type=args.video_type,
                    per_page=args.per_page, # Pass new argument
                    order=args.order # Pass new argument
                )
                log_entry = {
                    'timestamp': datetime.now().isoformat(),
                    'scene_key': scene_key,
                    'query': query,
                    'results': search_results
                }
                query_log.append(log_entry)
                
                if search_results and search_results['hits']:
                    for hit in search_results['hits']:
                        if hit['id'] not in downloaded_video_ids: # Check for duplicates
                            video_url = hit.get('videos', {}).get('large', {}).get('url')
                            if not video_url:
                                video_url = hit.get('videos', {}).get('medium', {}).get('url')
                            
                            if video_url:
                                # Temporary path for downloaded video before standardization
                                raw_video_filename = f"{scene_key}_{hit['id']}_raw.mp4"
                                raw_video_filepath = os.path.join(video_clips_dir, raw_video_filename)

                                # Path for standardized video
                                standardized_video_filename = f"{scene_key}_{hit['id']}_standardized.mp4"
                                standardized_video_filepath = os.path.join(video_clips_dir, standardized_video_filename)

                                if download_video(video_url, raw_video_filepath):
                                    print(f"Standardizing video: {raw_video_filepath}")
                                    if standardize_video_clip(raw_video_filepath, standardized_video_filepath):
                                        consolidated_analysis[scene_key]['video_info'] = {
                                            'id': hit['id'],
                                            'url': video_url,
                                            'tags': hit['tags'],
                                            'download_path': standardized_video_filepath # Store path to standardized video
                                        }
                                        downloaded_video_ids.add(hit['id']) # Add to set
                                        video_found = True
                                        # Clean up raw downloaded video
                                        os.remove(raw_video_filepath)
                                        break 
                time.sleep(1) # To avoid hitting API rate limits

        query_log_path = os.path.join(args.output_dir, config.QUERY_LOG_FILE)
        with open(query_log_path, 'w', encoding='utf-8') as f:
            json.dump(query_log, f, indent=4)

    # --- 4. Asset Preparation ---
    print("\n--- Phase 4: Asset Preparation ---")
    if not args.skip_downloads:
        adjusted_clips_dir = os.path.join(args.output_dir, config.ADJUSTED_CLIPS_DIR)
        os.makedirs(adjusted_clips_dir, exist_ok=True)

        for scene_key, scene_data in consolidated_analysis.items():
            if 'video_info' in scene_data and 'audio_info' in scene_data:
                print(f"Adjusting video for scene: {scene_key}")
                input_path = scene_data['video_info']['download_path']
                output_filename = f"{scene_key}_adjusted.mp4"
                output_path = os.path.join(adjusted_clips_dir, output_filename)
                target_duration = scene_data['audio_info']['duration']
                
                if adjust_video_duration(input_path, output_path, target_duration):
                    consolidated_analysis[scene_key]['adjusted_video_info'] = {
                        'path': output_path,
                        'duration': target_duration
                    }

    # --- 5. Final Output ---
    print("\n--- Phase 5: Final Output ---")
    final_json_path = os.path.join(args.output_dir, config.CONSOLIDATED_JSON_FILE)
    with open(final_json_path, 'w', encoding='utf-8') as f:
        json.dump(consolidated_analysis, f, indent=4)
        
    print(f"Processing complete. All assets and logs saved in: {args.output_dir}")

    # --- 6. Create Final Video ---
    print("\n--- Phase 6: Creating Final Video ---")
    create_final_video(consolidated_analysis, args.output_dir)

if __name__ == "__main__":
    main()
