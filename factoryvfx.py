import os
import random
import gc
import time
import re
from moviepy.editor import (VideoFileClip, TextClip, AudioFileClip, 
                          CompositeVideoClip, CompositeAudioClip, ImageClip,
                          concatenate_videoclips)
from moviepy.config import change_settings
from moviepy.editor import *
import moviepy.audio.fx.all as afx
import moviepy.video.fx.all as vfx  # MUST ADD THIS LINE

# CUSTOM MODULES
import subtitles
import brain
import artist
import voice

# 1. SETTINGS
MAGICK_PATH = r"C:\Program Files\ImageMagick-7.1.2-Q16-HDRI\magick.exe"
change_settings({"IMAGEMAGICK_BINARY": MAGICK_PATH})

CONFIG = {
    "output_folder": "ready_videos_advanced", 
    "temp_voice": "temp_voice_adv.mp3",
    "temp_img_folder": "temp_images", 
    "font": "arial",      
    "language": "en"         
}

# 2. HELPER FUNCTIONS

def split_text_into_segments(text):
    """Splits text into segments."""
    segments = re.split(r'(?<=[.,;:?!])\s+', text)
    return [s.strip() for s in segments if s.strip() and len(s) > 2]

def zoom_in_effect(clip, zoom_ratio=1.2):
    """Camera zoom-in effect."""
    return clip.resize(lambda t: 1 + (zoom_ratio - 1) * (t / clip.duration)).set_position('center')

def smart_resize(clip, target_w=1080, target_h=1920):
    """
    FIX: SMART RESIZE (REMOVES PILLARS)
    If image is narrow (1024px), scales to 1080px,
    cropping top/bottom to avoid black bars.
    """
    w, h = clip.size
    
    # Calculate ratios
    ratio_w = target_w / w
    ratio_h = target_h / h
    
    # Take the maximum to fill the ENTIRE screen
    scale = max(ratio_w, ratio_h)
    
    # Scale (with margin)
    clip_resized = clip.resize(scale)
    
    # Crop excess from the center
    clip_final = clip_resized.crop(x_center=clip_resized.w/2, 
                                   y_center=clip_resized.h/2, 
                                   width=target_w, 
                                   height=target_h)
    return clip_final

# 3. AUDIO ENGINE (Lore vs Alarm)
def create_audio_track(text, temp_voice_path, mode="lore"):
    """
    Prepares audio layer (Music + Intro + Voice), selecting music based on mode.
    """
    print(f"Calling voice.py module for voiceover...")
    
    # Voice generation
    success = voice.create_voice(text, temp_voice_path)
    if not success: 
        raise Exception("Voiceover error! Check voice.py")
    
    # Load voice
    voice_clip = AudioFileClip(temp_voice_path)
    
    # Offset variable
    voice_offset = 0.0
    audio_layers = []

    # INTRO LOGIC (RANDOM HOOK)
    intro_folder = os.path.join("assets", "intro")
    intro_path = None

    if os.path.exists(intro_folder) and os.listdir(intro_folder):
        random_intro = random.choice(os.listdir(intro_folder))
        intro_path = os.path.join(intro_folder, random_intro)
        print(f"Adding Random Hook (Intro): {random_intro}")
    
    if intro_path and os.path.exists(intro_path):
        intro_clip = AudioFileClip(intro_path)
        # Limit intro to max 3 seconds
        if intro_clip.duration > 3.0: intro_clip = intro_clip.subclip(0, 3.0)
        
        # VOICE OFFSET
        voice_offset = intro_clip.duration + 0.2
        voice_clip = voice_clip.set_start(voice_offset)
        
        audio_layers = [intro_clip, voice_clip]
        total_duration = voice_offset + voice_clip.duration + 2.0
    else:
        print("Intro not found, starting directly with voice.")
        audio_layers = [voice_clip]
        total_duration = voice_clip.duration + 2.0

    # DJ LOGIC (SMART MUSIC SELECTION)
    music_clip = None
    
    # Determine folder based on mode
    if mode == "alarm":
        music_folder = os.path.join("assets", "music", "alarm")
        print("DJ Mode: ALARM (Searching for sirens...)")
    else:
        music_folder = os.path.join("assets", "music", "lore")
        print("DJ Mode: LORE (Searching for ambient...)")

    # Fallback: If specific folder is missing, search in general folder
    if not os.path.exists(music_folder) or not os.listdir(music_folder):
        print(f"Folder {music_folder} is empty or doesn't exist! Searching in general assets/music...")
        music_folder = os.path.join("assets", "music")

    # Load track
    if os.path.exists(music_folder) and os.listdir(music_folder):
        random_music = random.choice(os.listdir(music_folder))
        music_path = os.path.join(music_folder, random_music)
        print(f"DJ HellReam selected track: {random_music}")
        
        # Loop to match video length
        if music_clip and music_clip.duration < total_duration:
            music_clip = afx.audio_loop(music_clip, duration=total_duration)
            
        music_clip = AudioFileClip(music_path).subclip(0, total_duration)
        
        # Volume: Sirens (Alarm) slightly louder, Ambient (Lore) quieter
        vol = 0.20 if mode == "alarm" else 0.15
        music_clip = music_clip.volumex(vol) 
        
        audio_layers.insert(0, music_clip)
    else:
        print("Music folder is empty or not found!")

    final_audio = CompositeAudioClip(audio_layers)
    
    clips_to_close = [voice_clip]
    if music_clip: clips_to_close.append(music_clip)
        
    return final_audio, total_duration, clips_to_close, voice_offset


# 4. VISUAL GENERATOR (UPDATED S.M.A.R.T. + AI DIRECTOR)
def create_visual_track(segments_list, total_duration, topic, mode="lore"):
    num_segments = len(segments_list)
    print(f"Visual track: {num_segments} scene(s).")
    
    # Calculate time per scene
    segment_duration = (total_duration / num_segments) + 1.5
    clips_to_stitch = []
    
    if not os.path.exists(CONFIG["temp_img_folder"]): os.makedirs(CONFIG["temp_img_folder"])

    for i, segment_text in enumerate(segments_list):
        print(f"\n Scene {i+1}/{num_segments}: '{segment_text[:20]}...'")
        
        # INSERT PAUSE HERE
        # If not the first scene, give a 5-second break to avoid rate limits
        if i > 0:
            print(" Waiting 5 sec to avoid rate limits...")
            time.sleep(5)

        img_path = os.path.join(CONFIG["temp_img_folder"], f"temp_seg_{i}.jpg")
        
        # MODIFICATION: CALL DIRECTOR
        print(f" Director analyzing text...")
        
        # Now the call is safe since we waited
        visual_prompt = brain.get_director_instruction(segment_text, topic)
        
        # ARTIST (Flux/Replicate)
        # Passing the ready instruction with camera angle
        success = artist.generate_horror_image(visual_prompt, img_path)
        
        if not success:
            if i > 0: img_path = os.path.join(CONFIG["temp_img_folder"], f"temp_seg_{i-1}.jpg")
            else: 
                print("Generation failed, and no previous image. Skipping.")
                continue 

        # Process image for video
        try:
            img_clip = ImageClip(img_path).set_duration(segment_duration)
            
            # Smart resize
            img_clip = smart_resize(img_clip, 1080, 1920)
            
            # BLACK AND WHITE FILTER (Mandatory for horror!)
            # If you want color, comment out the line below
            # img_clip = img_clip.fx(vfx.blackwhite) 

            # Zoom In animation
            zoomed_clip = zoom_in_effect(img_clip)
            
            # Crossfade transition
            if i > 0:
                zoomed_clip = zoomed_clip.crossfadein(1.0)
                
            clips_to_stitch.append(zoomed_clip)
            
        except Exception as e:
            print(f" Error processing video: {e}")
            continue

    print("Stitching scenes...")
    final_visual = concatenate_videoclips(clips_to_stitch, method="compose", padding=-1)
    
    # Match video length to audio
    if final_visual.duration > total_duration:
        final_visual = final_visual.subclip(0, total_duration)
    else:
        final_visual = final_visual.set_duration(total_duration)
    
    return final_visual, clips_to_stitch

def apply_random_overlay(base_clip):
    """Applies random effect (grain, glitches)."""
    overlay_folder = os.path.join("assets", "overlays")
    
    if not os.path.exists(overlay_folder) or not os.listdir(overlay_folder):
        print("Overlays not found, skipping...")
        return base_clip

    try:
        overlay_name = random.choice(os.listdir(overlay_folder))
        overlay_path = os.path.join(overlay_folder, overlay_name)
        print(f"Applying VFX: {overlay_name}")

        overlay = VideoFileClip(overlay_path)
        
        # Smart resize overlay to fit perfectly
        overlay = smart_resize(overlay, 1080, 1920)
        
        overlay = overlay.loop(duration=base_clip.duration)
        overlay = overlay.set_opacity(0.25) # Effect opacity

        final = CompositeVideoClip([base_clip, overlay])
        return final

    except Exception as e:
        print(f"VFX Error: {e}")
        return base_clip 


# 5. MAIN MANAGER

def main():
    if not os.path.exists(CONFIG["output_folder"]): os.makedirs(CONFIG["output_folder"])

    print("Activation: AI-Stories (Acer Nitro Edition)...")
    
    # MODE SELECTION MENU
    print("\nSelect video mode:")
    print(" [1] LORE (Story/Facts)")
    print(" [2] ALARM (Rules/Alert)")
    choice = input("Your choice (1 or 2): ")
    
    mode = "lore" # Default
    target_count = 4
    if choice == "2":
        mode = "alarm"
        target_count = 6 # Need more items for rules
    
    # 1. ASK FOR TOPIC (for text and image generation)
    topic = input(f"\nVideo topic ({mode.upper()}): ")

    # 2. ASK FOR TITLE SEPARATELY
    custom_title = input("Text for TITLE (Leave empty for auto): ")
    
    # Text generation
    quotes = brain.get_ai_quotes(topic, mode=mode, count=target_count)
    
    if not quotes:
        print("Brain error. Script is empty.")
        return

    # Combine text for voiceover
    full_text_for_voice = " ".join(quotes)
    
    print(f"\nReceived scenes: {len(quotes)}")
    for idx, s in enumerate(quotes):
        print(f"  {idx+1}. {s}")

    final_video_clip = None
    bg_visual_clip = None
    segment_clips_to_close = []
    text_clips_to_close = []
    audio_res_to_close = []

    try:
        print("Audio (Music + Voice + Hook)...")
        final_audio, duration, audio_res_to_close, voice_offset = create_audio_track(
            full_text_for_voice, CONFIG["temp_voice"], mode=mode
        )

        print("Visual (Local GPU Rendering)...")
        bg_visual_clip, segment_clips_to_close = create_visual_track(quotes, duration, topic, mode=mode)
        
        # VFX: OVERLAY
        print("Adding film effects...")
        bg_visual_clip = apply_random_overlay(bg_visual_clip)
        
        # SUBTITLES
        subtitle_font_param = "Special-Elite-Regular"
        print(f"Creating subtitles ({subtitle_font_param})...")

        title_filename = "Anton.ttf"
        title_font_param = title_filename if os.path.exists(title_filename) else "Arial"

        text_clips_to_close = subtitles.create_karaoke_clips(CONFIG["temp_voice"], subtitle_font_param)
        text_clips_to_close = [clip.set_position(('center', 1200)) for clip in text_clips_to_close]
        
        if voice_offset > 0:
            text_clips_to_close = [clip.set_start(clip.start + voice_offset) for clip in text_clips_to_close]

        print("Assembling final video...")
        
        title_clip = None
        try:
            # TITLE LOGIC
            # If user entered custom text, use it.
            # If not, take the first word from the topic.
            if custom_title.strip():
                title_text = custom_title.upper()
            else:
                title_text = topic.split(',')[0].upper()

            title_duration = voice_offset if voice_offset > 0.5 else 2.0
            
            if title_text:
                print(f"Red title: {title_text}")
                title_clip = TextClip(
                    title_text, 
                    fontsize=110, 
                    color='red', 
                    font=title_font_param,
                    method='caption',
                    size=(1000, None)
                ).set_position('center').set_start(0).set_duration(title_duration)
                
                final_layers = [bg_visual_clip, title_clip] + text_clips_to_close
            else:
                final_layers = [bg_visual_clip] + text_clips_to_close

        except Exception as e:
            print(f"Title Error: {e}")
            final_layers = [bg_visual_clip] + text_clips_to_close

        final_video_clip = CompositeVideoClip(final_layers)
        final_video_clip = final_video_clip.set_audio(final_audio)

        print("Rendering (This may take some time)...")
        final_video_clip = final_video_clip.fadeout(1.0)
        final_video_clip = final_video_clip.audio_fadeout(1.0)

        output_name = f"HellReam_{mode}_{int(time.time())}.mp4"
        output_path = os.path.join(CONFIG["output_folder"], output_name)
        
        final_video_clip.write_videofile(
            output_path,
            fps=24,
            codec='libx264',
            preset='medium', # Slightly higher quality render
            threads=8,
            verbose=False,
            logger=None)
        print(f"\nDONE! Video saved: {output_path}")

    except Exception as e:
        print(f"\nCRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        print("\nCleaning up temporary files...")
        if final_video_clip: final_video_clip.close()
        if bg_visual_clip: bg_visual_clip.close()
        if title_clip: title_clip.close()
        for clip in segment_clips_to_close: clip.close()
        for clip in text_clips_to_close: clip.close()
        for res in audio_res_to_close: res.close()
        
        if os.path.exists(CONFIG["temp_voice"]):
            try: os.remove(CONFIG["temp_voice"])
            except: pass
        if os.path.exists(CONFIG["temp_img_folder"]):
            for img_file in os.listdir(CONFIG["temp_img_folder"]):
                try: os.remove(os.path.join(CONFIG["temp_img_folder"], img_file))
                except: pass
            try: os.rmdir(CONFIG["temp_img_folder"])
            except: pass

        gc.collect()

if __name__ == "__main__":
    main()