import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import FastAPI, UploadFile, File, BackgroundTasks
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from utils import get_video_metadata, generate_thumbnail, generate_preview, generate_timeline_sprites

app = FastAPI()

# Paths for storing media and assets
VIDEO_FOLDER = "videos"
THUMBNAIL_FOLDER = "thumbnails"
PREVIEW_FOLDER = "previews"
SPRITE_FOLDER = "sprites"

# Thread pool for background asset generation
executor = ThreadPoolExecutor(max_workers=2)

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

def generate_assets_for_video(video_path, filename):
    """Generate all assets for a single video (runs in background thread)."""
    basename = os.path.splitext(filename)[0]
    
    # Paths for assets
    thumb_path = os.path.join(THUMBNAIL_FOLDER, f"{basename}.jpg")
    preview_path = os.path.join(PREVIEW_FOLDER, f"{basename}.mp4")
    
    try:
        print(f"Background processing: {filename}")
        
        # Generate assets if they don't exist
        if not os.path.exists(thumb_path):
            generate_thumbnail(video_path, thumb_path)
        
        if not os.path.exists(preview_path):
            generate_preview(video_path, preview_path)
        
        # Generate sprites
        generate_timeline_sprites(video_path, SPRITE_FOLDER, filename)
        
        print(f"Completed background processing: {filename}")
        
    except Exception as e:
        print(f"Error processing {filename}: {e}")

@app.get("/media/list")
def list_videos(background_tasks: BackgroundTasks):
    """Returns a list of all videos with metadata, schedules asset generation in background."""
    videos = []
    
    for filename in os.listdir(VIDEO_FOLDER):
        if not filename.lower().endswith((".mp4", ".mkv", ".mov", ".webm")):
            continue

        path = os.path.join(VIDEO_FOLDER, filename)
        basename = os.path.splitext(filename)[0]

        # Check if assets exist
        thumb_path = os.path.join(THUMBNAIL_FOLDER, f"{basename}.jpg")
        preview_path = os.path.join(PREVIEW_FOLDER, f"{basename}.mp4")
        
        # Use placeholder or actual paths
        thumbnail_url = f"/thumbnails/{basename}.jpg" if os.path.exists(thumb_path) else None
        preview_url = f"/previews/{basename}.mp4" if os.path.exists(preview_path) else None
        
        # Get metadata (this is fast)
        metadata = get_video_metadata(path)
        
        videos.append({
            "filename": filename,
            "title": basename,
            "thumbnail": thumbnail_url,
            "preview": preview_url,
            "metadata": metadata,
            "assets_ready": os.path.exists(thumb_path) and os.path.exists(preview_path)
        })
        
        # Schedule background asset generation if assets don't exist
        if not os.path.exists(thumb_path) or not os.path.exists(preview_path):
            background_tasks.add_task(generate_assets_for_video, path, filename)
    
    return videos

@app.get("/media/status/{filename}")
def get_video_status(filename: str):
    """Check if assets are ready for a specific video."""
    basename = os.path.splitext(filename)[0]
    thumb_path = os.path.join(THUMBNAIL_FOLDER, f"{basename}.jpg")
    preview_path = os.path.join(PREVIEW_FOLDER, f"{basename}.mp4")
    
    return {
        "filename": filename,
        "thumbnail_ready": os.path.exists(thumb_path),
        "preview_ready": os.path.exists(preview_path),
        "assets_ready": os.path.exists(thumb_path) and os.path.exists(preview_path)
    }

@app.post("/upload")
async def upload_video(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    """Upload new video file via drag-and-drop."""
    dest = os.path.join(VIDEO_FOLDER, file.filename)
    with open(dest, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Schedule background asset generation for the new video
    if background_tasks:
        background_tasks.add_task(generate_assets_for_video, dest, file.filename)
    
    return {"filename": file.filename}

@app.get("/", response_class=HTMLResponse)
def serve_homepage():
    with open("static/index.html", "r", encoding="utf-8") as f:
        return f.read()