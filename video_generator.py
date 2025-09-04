from moviepy.editor import TextClip, CompositeVideoClip, AudioFileClip, concatenate_videoclips, ColorClip
import os
import secrets

def generate_video_from_products(products, audio_path, output_dir="static/videos"):
    """
    Generate landscape and portrait videos from products using an existing TTS audio file.

    Args:
        products (list): List of product dicts with at least a 'title' or 'description'.
        audio_path (str): Path to an existing audio file (TTS already generated).
        output_dir (str): Directory to save generated videos.

    Returns:
        dict: Paths to generated landscape and portrait videos.
    """
    os.makedirs(output_dir, exist_ok=True)
    duration_per_clip = 5  # seconds per product slide

    # Prepare video clips
    clips_landscape = []
    clips_portrait = []

    for product in products:
        title = product.get("title") or product.get("description") or "No Title"

        # Landscape 1280x720
        bg_land = ColorClip(size=(1280, 720), color=(0, 0, 0), duration=duration_per_clip)
        txt_land = TextClip(
            title, fontsize=50, color="white", method="caption", size=(1280, 720)
        ).set_duration(duration_per_clip).set_position("center")
        clips_landscape.append(CompositeVideoClip([bg_land, txt_land]))

        # Portrait 720x1280
        bg_port = ColorClip(size=(720, 1280), color=(0, 0, 0), duration=duration_per_clip)
        txt_port = TextClip(
            title, fontsize=50, color="white", method="caption", size=(720, 1280)
        ).set_duration(duration_per_clip).set_position("center")
        clips_portrait.append(CompositeVideoClip([bg_port, txt_port]))

    # Concatenate slides
    video_land = (
        concatenate_videoclips(clips_landscape, method="compose")
        if clips_landscape
        else ColorClip(size=(1280, 720), color=(0, 0, 0), duration=5)
    )
    video_port = (
        concatenate_videoclips(clips_portrait, method="compose")
        if clips_portrait
        else ColorClip(size=(720, 1280), color=(0, 0, 0), duration=5)
    )

    # Attach TTS audio
    if os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        video_land = video_land.set_audio(audio).set_duration(audio.duration)
        video_port = video_port.set_audio(audio).set_duration(audio.duration)
    else:
        print(f"⚠️ Audio file {audio_path} not found. Videos will have no audio.")

    # Save videos with unique filenames
    token = secrets.token_hex(4)
    path_land = os.path.join(output_dir, f"video_landscape_{token}.mp4")
    path_port = os.path.join(output_dir, f"video_portrait_{token}.mp4")

    video_land.write_videofile(path_land, fps=24)
    video_port.write_videofile(path_port, fps=24)

    return {"landscape": path_land, "portrait": path_port}
