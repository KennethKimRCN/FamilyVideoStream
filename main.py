from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os
from utils import get_video_metadata, generate_thumbnail, generate_preview

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE = os.getcwd()
VIDEO_FOLDER = os.path.join(BASE, "videos")
THUMB_FOLDER = os.path.join(BASE, "thumbnails")
PREVIEW_FOLDER = os.path.join(BASE, "previews")

app.mount("/videos", StaticFiles(directory=VIDEO_FOLDER), name="videos")
app.mount("/thumbnails", StaticFiles(directory=THUMB_FOLDER), name="thumbnails")
app.mount("/previews", StaticFiles(directory=PREVIEW_FOLDER), name="previews")

@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    with open("index.html", "r", encoding="utf-8") as f:
        return f.read()

@app.get("/media/list")
def list_videos():
    results = []
    for filename in os.listdir(VIDEO_FOLDER):
        if filename.lower().endswith((".mp4", ".mov", ".mkv")):
            path = os.path.join(VIDEO_FOLDER, filename)
            thumb_path = os.path.join(THUMB_FOLDER, filename + ".jpg")
            preview_path = os.path.join(PREVIEW_FOLDER, filename + ".mp4")

            generate_thumbnail(path, thumb_path)
            generate_preview(path, preview_path)

            metadata = get_video_metadata(path)
            video_info = {
                "title": filename.rsplit(".", 1)[0],
                "filename": filename,
                "thumbnail": f"/thumbnails/{filename}.jpg",
                "preview": f"/previews/{filename}.mp4",
                "metadata": metadata
            }
            results.append(video_info)
    return results
