import os
import subprocess
import json

def log_output(label, result):
    """Save FFmpeg stdout/stderr to a log file"""
    with open("ffmpeg.log", "a", encoding="utf-8") as log:
        log.write(f"\n[{label}]\n")
        log.write(result.stdout)
        log.write(result.stderr)
        log.write("\n")

def get_video_metadata(path):
    """Extract video metadata using ffprobe"""
    cmd = [
        "ffprobe", "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,duration,codec_name",
        "-show_entries", "format=size",
        "-of", "json", path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    log_output(f"METADATA {path}", result)

    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError:
        return {}

def generate_thumbnail(video_path, thumb_path, timestamp="00:00:10"):
    """Generate a single-frame thumbnail image"""
    if not os.path.exists(thumb_path):
        print(f"Generating thumbnail: {thumb_path}")
        result = subprocess.run([
            "ffmpeg", "-y", "-ss", timestamp, "-i", video_path,
            "-vframes", "1", "-q:v", "2", thumb_path
        ], capture_output=True, text=True)
        log_output(f"THUMBNAIL {video_path}", result)

def generate_preview(video_path, preview_path, start="00:00:05", duration="5"):
    """Generate a 5-second preview clip"""
    if not os.path.exists(preview_path):
        print(f"Generating preview: {preview_path}")
        result = subprocess.run([
            "ffmpeg", "-y", "-ss", start, "-t", duration, "-i", video_path,
            "-c:v", "libx264", "-an", "-preset", "fast", "-crf", "28", preview_path
        ], capture_output=True, text=True)
        log_output(f"PREVIEW {video_path}", result)
