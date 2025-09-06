import requests
import os
import moviepy.editor as mp
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

def generate_queries(scene_analysis, overall_settings):
    """
    Generates search queries for a scene based on its analysis.
    """
    sub_queries = []
    
    hf_emotion = scene_analysis.get('emotion', {})
    vader_sentiment = scene_analysis.get('sentiment', {})
    entity_info = scene_analysis.get('entities', {})
    scene_nouns = [noun for noun in entity_info.get('nouns', []) if noun.lower() != 'scene']
    scene_verbs = [verb for verb in entity_info.get('verbs', [])]
    scene_adverbs = [adverb for adverb in entity_info.get('adverbs', [])]
    
    overall_locations = overall_settings.get('locations', [])
    overall_atmosphere = overall_settings.get('atmosphere', [])

    # Primary query: Combine key entities and relevant emotional terms
    query_terms_primary = []
    
    # Always include "father" and "son" for this specific use case
    query_terms_primary.append('father')
    query_terms_primary.append('son')
    query_terms_primary.append('people') # Add "people" to prioritize videos with humans

    # Add top nouns and verbs
    query_terms_primary.extend([term.lower() for term in scene_nouns[:3]])
    query_terms_primary.extend([term.lower() for term in scene_verbs[:3]])

    # Add emotional terms based on sentiment/emotion analysis
    if hf_emotion and 'label' in hf_emotion:
        if hf_emotion['label'] in ['optimism', 'joy', 'love']:
            query_terms_primary.append('happy')
        elif hf_emotion['label'] in ['sadness', 'anger', 'fear']:
            query_terms_primary.append('struggle')

    if vader_sentiment and 'dominant_emotion' in vader_sentiment:
        if vader_sentiment['dominant_emotion'] == 'Positive':
            query_terms_primary.append('love')
        elif vader_sentiment['dominant_emotion'] == 'Negative':
            query_terms_primary.append('sad')

    # Add overall settings if present
    query_terms_primary.extend([term.lower() for term in overall_locations])
    query_terms_primary.extend([term.lower() for term in overall_atmosphere])

    # Ensure unique terms and limit to 5
    if query_terms_primary:
        sub_queries.append(' '.join(list(dict.fromkeys([term for term in query_terms_primary if term and not term.isdigit()]))[:5]))
    
    # Fallback query: If no specific queries are generated, use general terms
    if not sub_queries:
        fallback_terms = []
        if scene_nouns:
            fallback_terms.append(scene_nouns[0].lower()) # Use the first noun as a fallback
        if scene_verbs:
            fallback_terms.append(scene_verbs[0].lower()) # Use the first verb as a fallback
        if fallback_terms:
            sub_queries.append(' '.join(fallback_terms))
        else:
            sub_queries.append("family life") # Default general query

    return list(dict.fromkeys(sub_queries))

def search_videos(query, api_key, is_g_rated=False, video_type='film', per_page=200, order='latest'):
    """
    Searches for vertical videos on Pixabay.
    """
    endpoint_url = "https://pixabay.com/api/videos/"
    params = {
        'key': api_key,
        'q': query,
        'orientation': 'vertical', # Ensure this is always vertical
        'safesearch': 'true' if is_g_rated else 'false', # Corrected safesearch
        'video_type': video_type,
        'editors_choice': 'true', # Keep hardcoded for now, will make configurable later
        'per_page': per_page, # Added per_page
        'order': order # Added order
    }

    try:
        response = requests.get(endpoint_url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error during Pixabay API request: {e}")
        return None

def download_video(video_url, save_path):
    """
    Downloads a video from a URL.
    """
    try:
        video_response = requests.get(video_url, stream=True)
        video_response.raise_for_status()
        with open(save_path, 'wb') as vf:
            for chunk in video_response.iter_content(chunk_size=8192):
                vf.write(chunk)
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error downloading video: {e}")
        return False

def standardize_video_clip(input_path, output_path, target_resolution=(1080, 1920), target_fps=30):
    """
    Standardizes a video clip to a target resolution and frame rate.
    """
    clip = None
    try:
        clip = mp.VideoFileClip(input_path)
        
        # Resize if necessary
        if clip.size != target_resolution:
            clip = clip.resize(newsize=target_resolution)
            
        # Set FPS
        clip = clip.set_fps(target_fps)
        
        clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
        return True
    except Exception as e:
        print(f"Error standardizing video clip {input_path}: {e}")
        return False
    finally:
        if clip:
            clip.close()

def adjust_video_duration(input_path, output_path, target_duration):
    """
    Adjusts the duration of a video to match the target duration.
    """
    original_clip = None
    looped_clip = None
    remaining_clip = None
    clip_to_save = None
    try:
        original_clip = mp.VideoFileClip(input_path)
        original_duration = original_clip.duration

        # Round target_duration to avoid floating point issues
        target_duration = round(target_duration, 2) # Round to two decimal places (centiseconds)

        if target_duration < original_duration:
            clip_to_save = original_clip.subclip(0, target_duration)
        elif target_duration > original_duration:
            num_loops = int(target_duration // original_duration)
            remaining_duration = target_duration % original_duration
            
            looped_clip = original_clip.fx(mp.vfx.loop, duration=original_duration * num_loops) if num_loops > 0 else original_clip
            
            if remaining_duration > 0:
                remaining_clip = original_clip.subclip(0, remaining_duration)
                clip_to_save = mp.concatenate_videoclips([looped_clip, remaining_clip]) if num_loops > 0 else remaining_clip
            else:
                clip_to_save = looped_clip
            
            clip_to_save = clip_to_save.set_duration(target_duration)
        else:
            clip_to_save = original_clip

        clip_to_save.write_videofile(output_path, codec='libx264', audio_codec='aac')
        
        return True
    except Exception as e:
        print(f"Error adjusting video duration: {e}")
        return False
    finally:
        if original_clip:
            original_clip.close()
        if looped_clip and looped_clip != original_clip:
            looped_clip.close()
        if remaining_clip:
            remaining_clip.close()
        if clip_to_save and clip_to_save != original_clip:
            clip_to_save.close()

def create_final_video(consolidated_data, output_dir):
    """
    Combines the adjusted video clips and audio files into a final video.
    """
    video_clips = []
    audio_clips = []
    final_video_clip = None
    final_audio_clip = None
    
    try:
        # Sort scenes by key to ensure correct order
        sorted_scenes = sorted(consolidated_data.items(), key=lambda item: item[0])

        for scene_key, scene_data in sorted_scenes:
            if scene_key.startswith('S') and 'adjusted_video_info' in scene_data and 'audio_info' in scene_data:
                adjusted_video_path = scene_data['adjusted_video_info'].get('path')
                audio_path = scene_data['audio_info'].get('filename')

                if adjusted_video_path and audio_path and os.path.exists(adjusted_video_path) and os.path.exists(audio_path):
                    print(f"Processing scene {scene_key} for final video.")
                    video_clips.append(mp.VideoFileClip(adjusted_video_path))
                    audio_clips.append(mp.AudioFileClip(audio_path))
                else:
                    print(f"Warning: Missing adjusted video or audio for scene {scene_key}. Skipping.")

        if video_clips:
            final_video_clip = mp.concatenate_videoclips(video_clips)
            final_audio_clip = mp.concatenate_audioclips(audio_clips)
            
            final_video_clip = final_video_clip.set_audio(final_audio_clip)
            
            final_video_path = os.path.join(output_dir, "final_youtube_short.mp4")
            
            print(f"\nSaving final video to: {final_video_path}")
            final_video_clip.write_videofile(final_video_path, codec='libx264', audio_codec='aac')
            
            return final_video_path, final_video_clip.duration
            
        return None, 0
    except Exception as e:
        print(f"Error creating final video: {e}")
        return None, 0
    finally:
        for clip in video_clips:
            clip.close()
        for clip in audio_clips:
            clip.close()
        if final_video_clip:
            final_video_clip.close()
        if final_audio_clip:
            final_audio_clip.close()
