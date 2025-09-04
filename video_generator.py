from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips, ColorClip
from gtts import gTTS
import os
import secrets

def generate_video_pipeline(user_text, products, output_dir="static/videos", tts_lang="en"):
    """
    Generate landscape and portrait videos from products using user-provided text for TTS.
    
    Args:
        user_text (str): The text the user wants to use for TTS.
        products (list): List of product dicts with at least a 'title' key.
        output_dir (str): Directory to save generated videos.
        tts_lang (str): Language for TTS (default 'en').
    
    Returns:
        dict: Paths to generated landscape and portrait videos.
    """
    os.makedirs(output_dir, exist_ok=True)
    duration_per_clip = 5  # seconds per product slide

    # Step 1: Generate TTS audio
    audio_file = f"user_tts_{secrets.token_hex(4)}.mp3"
    audio_path = os.path.join(output_dir, audio_file)
    tts = gTTS(text=user_text, lang=tts_lang)
    tts.save(audio_path)

    # Step 2: Prepare clips
    clips_landscape = []
    clips_portrait = []

    for product in products:
        title = product.get('title', 'No Title')

        # Landscape 1280x720
        bg_land = ColorClip(size=(1280,720), color=(0,0,0), duration=duration_per_clip)
        txt_land = TextClip(title, fontsize=50, color='white', method='caption', size=(1280,720)).set_duration(duration_per_clip).set_position("center")
        clips_landscape.append(CompositeVideoClip([bg_land, txt_land]))

        # Portrait 720x1280
        bg_port = ColorClip(size=(720,1280), color=(0,0,0), duration=duration_per_clip)
        txt_port = TextClip(title, fontsize=50, color='white', method='caption', size=(720,1280)).set_duration(duration_per_clip).set_position("center")
        clips_portrait.append(CompositeVideoClip([bg_port, txt_port]))

    # Step 3: Concatenate clips
    video_land = concatenate_videoclips(clips_landscape, method="compose") if clips_landscape else ColorClip(size=(1280,720), color=(0,0,0), duration=5)
    video_port = concatenate_videoclips(clips_portrait, method="compose") if clips_portrait else ColorClip(size=(720,1280), color=(0,0,0), duration=5)

    # Step 4: Attach TTS audio
    if os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        video_land = video_land.set_audio(audio).set_duration(audio.duration)
        video_port = video_port.set_audio(audio).set_duration(audio.duration)
    else:
        print(f"⚠️ Audio file {audio_path} not found. Videos will have no audio.")

    # Step 5: Save videos with unique filenames
    token = secrets.token_hex(4)
    path_land = os.path.join(output_dir, f"video_landscape_{token}.mp4")
    path_port = os.path.join(output_dir, f"video_portrait_{token}.mp4")

    video_land.write_videofile(path_land, fps=24)
    video_port.write_videofile(path_port, fps=24)

    return {"landscape": path_land, "portrait": path_port, "audio": audio_path}
