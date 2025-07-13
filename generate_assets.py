import os
from utils import generate_thumbnail, generate_preview, get_video_metadata

VIDEO_FOLDER = "videos"
THUMB_FOLDER = "thumbnails"
PREVIEW_FOLDER = "previews"

def generate_for_all():
    for filename in os.listdir(VIDEO_FOLDER):
        if filename.lower().endswith((".mp4", ".mov", ".mkv", ".webm")):
            video_path = os.path.join(VIDEO_FOLDER, filename)
            thumb_path = os.path.join(THUMB_FOLDER, filename + ".jpg")
            preview_path = os.path.join(PREVIEW_FOLDER, filename + ".mp4")

            print(f"Processing: {filename}")
            generate_thumbnail(video_path, thumb_path)
            generate_preview(video_path, preview_path)
            meta = get_video_metadata(video_path)
            print(f"→ Duration: {meta['streams'][0]['duration']} sec")

if __name__ == "__main__":
    generate_for_all()

## python Generate_assets.py
## This will generate the thumbnails in the background