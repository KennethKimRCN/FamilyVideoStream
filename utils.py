import os
import subprocess
import json

def log_output(label, result):
    """Log FFmpeg stdout and stderr for debugging."""
    with open("ffmpeg.log", "a", encoding="utf-8") as log:
        log.write(f"\n[{label}]\n")
        log.write(result.stdout)
        log.write(result.stderr)
        log.write("\n")

def try_ffmpeg_cmd(cmd_gpu, cmd_cpu, label):
    """
    Try FFmpeg command with GPU first.
    If it fails (non-zero return or error message), retry with CPU.
    """
    result = subprocess.run(cmd_gpu, capture_output=True, text=True)
    log_output(f"{label} (GPU)", result)

    if result.returncode != 0 or "error" in result.stderr.lower():
        print(f"[Fallback] {label} failed on GPU. Trying CPU version...")
        result = subprocess.run(cmd_cpu, capture_output=True, text=True)
        log_output(f"{label} (CPU)", result)

def get_video_duration(video_path):
    """Get video duration in seconds."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0", video_path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    try:
        return float(result.stdout.strip())
    except (ValueError, AttributeError):
        return 0

def get_video_metadata(path):
    """
    Extract metadata like width, height, duration, codec using ffprobe.
    Returns a dictionary.
    """
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,duration,codec_name",
        "-show_entries", "format=duration,size,bit_rate",
        "-of", "json", path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log_output(f"METADATA {path}", result)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}

def generate_thumbnail(video_path, thumb_path, timestamp=None):
    """
    Capture a single frame at the given timestamp and save as a JPG thumbnail.
    Automatically calculates safe timestamp based on video duration.
    Tries GPU decoding first, falls back to CPU.
    """
    if os.path.exists(thumb_path):
        return

    print(f"Generating thumbnail: {thumb_path}")
    
    # Get video duration and calculate safe timestamp
    duration = get_video_duration(video_path)
    if duration <= 0:
        print(f"Warning: Could not get duration for {video_path}")
        timestamp = "00:00:01"
    elif timestamp is None:
        # Use 10% of video duration, but at least 1 second and max 10 seconds
        safe_time = max(1, min(duration * 0.1, 10))
        if safe_time >= duration:
            safe_time = max(0.5, duration - 1)  # Go to near the end if video is very short
        timestamp = f"{int(safe_time//3600):02d}:{int((safe_time%3600)//60):02d}:{safe_time%60:06.3f}"

    cmd_gpu = [
        "ffmpeg", "-y", "-hwaccel", "cuda", "-ss", timestamp,
        "-i", video_path,
        "-vframes", "1", "-q:v", "2", thumb_path
    ]

    cmd_cpu = [
        "ffmpeg", "-y", "-ss", timestamp,
        "-i", video_path,
        "-vframes", "1", "-q:v", "2", thumb_path
    ]

    try_ffmpeg_cmd(cmd_gpu, cmd_cpu, f"THUMBNAIL {video_path}")

def generate_preview(video_path, preview_path, start=None, duration=None):
    """
    Create a short preview clip using NVENC if possible.
    Automatically calculates safe start time and duration based on video length.
    Tries GPU encoding first, falls back to CPU.
    """
    if os.path.exists(preview_path):
        return

    print(f"Generating preview: {preview_path}")
    
    # Get video duration and calculate safe parameters
    video_duration = get_video_duration(video_path)
    if video_duration <= 0:
        print(f"Warning: Could not get duration for {video_path}")
        start = "00:00:00"
        duration = "3"
    else:
        if start is None:
            # Start at 10% of video duration, but at least 1 second
            start_time = max(1, min(video_duration * 0.1, 5))
            if start_time >= video_duration:
                start_time = 0  # Start from beginning if video is very short
            start = f"{int(start_time//3600):02d}:{int((start_time%3600)//60):02d}:{start_time%60:06.3f}"
        
        if duration is None:
            # Preview duration should be min(5 seconds, 80% of remaining video)
            remaining_duration = video_duration - (start_time if 'start_time' in locals() else 1)
            preview_duration = min(5, max(1, remaining_duration * 0.8))
            duration = str(int(preview_duration))

    cmd_gpu = [
        "ffmpeg", "-y", "-hwaccel", "cuda", "-ss", start, "-t", duration,
        "-i", video_path,
        "-c:v", "h264_nvenc", "-preset", "fast", "-an",
        preview_path
    ]

    cmd_cpu = [
        "ffmpeg", "-y", "-ss", start, "-t", duration,
        "-i", video_path,
        "-c:v", "libx264", "-preset", "fast", "-an",
        preview_path
    ]

    try_ffmpeg_cmd(cmd_gpu, cmd_cpu, f"PREVIEW {video_path}")

def generate_timeline_sprites(video_path, output_dir, basename, interval=5):
    """
    Generate small thumbnails every X seconds of video starting from the beginning.
    Automatically adjusts interval for very short videos.
    Saved as JPGs like video_000.jpg, video_001.jpg, ...
    Tries GPU decoding first, falls back to CPU.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{basename}_%03d.jpg")

    print(f"Generating timeline sprites: {output_path}")
    
    # Get video duration and adjust interval if needed
    duration = get_video_duration(video_path)
    if duration <= 0:
        print(f"Warning: Could not get duration for {video_path}")
        interval = 5
    else:
        # For very short videos, use smaller intervals
        if duration < 30:  # Less than 30 seconds
            interval = max(1, duration / 10)  # Create ~10 sprites
        elif duration < 60:  # Less than 1 minute
            interval = 3
        # For longer videos, keep the default interval

    cmd_gpu = [
        "ffmpeg", "-y", "-hwaccel", "cuda",
        "-i", video_path,
        "-vf", f"fps=1/{interval},scale=160:-1",
        "-qscale:v", "2", output_path
    ]

    cmd_cpu = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-vf", f"fps=1/{interval},scale=160:-1",
        "-qscale:v", "2", output_path
    ]

    try_ffmpeg_cmd(cmd_gpu, cmd_cpu, f"SPRITES {video_path}")

def format_timestamp(seconds):
    """Convert seconds to HH:MM:SS.mmm format."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"