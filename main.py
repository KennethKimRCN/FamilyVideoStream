import os
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from utils import get_video_metadata, generate_thumbnail, generate_preview, generate_timeline_sprites

app = FastAPI()

# Paths for storing media and assets
VIDEO_FOLDER = "videos"
THUMBNAIL_FOLDER = "thumbnails"
PREVIEW_FOLDER = "previews"
SPRITE_FOLDER = "sprites"

# Allow cross-origin requests (for front-end dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# Serve static files for each folder
app.mount("/videos", StaticFiles(directory=VIDEO_FOLDER), name="videos")
app.mount("/thumbnails", StaticFiles(directory=THUMBNAIL_FOLDER), name="thumbnails")
app.mount("/previews", StaticFiles(directory=PREVIEW_FOLDER), name="previews")
app.mount("/sprites", StaticFiles(directory=SPRITE_FOLDER), name="sprites")

# Ensure folders exist
os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(THUMBNAIL_FOLDER, exist_ok=True)
os.makedirs(PREVIEW_FOLDER, exist_ok=True)
os.makedirs(SPRITE_FOLDER, exist_ok=True)

@app.get("/media/list")
def list_videos():
    """Returns a list of all videos with metadata, thumbnail, and preview paths."""
    videos = []
    for filename in os.listdir(VIDEO_FOLDER):
        if not filename.lower().endswith((".mp4", ".mkv", ".mov")):
            continue

        path = os.path.join(VIDEO_FOLDER, filename)
        basename = os.path.splitext(filename)[0]

        # Paths
        thumb_path = os.path.join(THUMBNAIL_FOLDER, f"{basename}.jpg")
        preview_path = os.path.join(PREVIEW_FOLDER, f"{basename}.mp4")

        # Generate assets
        generate_thumbnail(path, thumb_path)
        generate_preview(path, preview_path)
        generate_timeline_sprites(path, SPRITE_FOLDER, filename)

        metadata = get_video_metadata(path)

        videos.append({
            "filename": filename,
            "title": basename,
            "thumbnail": f"/thumbnails/{basename}.jpg",
            "preview": f"/previews/{basename}.mp4",
            "metadata": metadata
        })
    return videos

@app.post("/upload")
async def upload_video(file: UploadFile = File(...)):
    """Upload new video file via drag-and-drop."""
    dest = os.path.join(VIDEO_FOLDER, file.filename)
    with open(dest, "wb") as f:
        content = await file.read()
        f.write(content)
    return {"filename": file.filename}


from fastapi.responses import HTMLResponse

@app.get("/", response_class=HTMLResponse)
def serve_homepage():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()
