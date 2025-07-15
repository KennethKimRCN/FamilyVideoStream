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

def generate_thumbnail(video_path, thumb_path, timestamp="00:00:10"):
    """
    Capture a single frame at the given timestamp and save as a JPG thumbnail.
    Tries GPU decoding first, falls back to CPU.
    """
    if os.path.exists(thumb_path):
        return

    print(f"Generating thumbnail: {thumb_path}")

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

def generate_preview(video_path, preview_path, start="00:00:05", duration="5"):
    """
    Create a short preview clip using NVENC if possible.
    Tries GPU encoding first, falls back to CPU.
    """
    if os.path.exists(preview_path):
        return

    print(f"Generating preview: {preview_path}")

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
    Generate small thumbnails every X seconds of video.
    Saved as JPGs like video_000.jpg, video_001.jpg, ...
    Tries GPU decoding first, falls back to CPU.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, f"{basename}_%03d.jpg")

    print(f"Generating timeline sprites: {output_path}")

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
