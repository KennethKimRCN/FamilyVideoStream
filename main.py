from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI()

# Allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use "*" for dev; restrict in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

VIDEO_FOLDER = os.path.join(os.getcwd(), "videos")
app.mount("/videos", StaticFiles(directory=VIDEO_FOLDER), name="videos")

@app.get("/")
async def index():
    return {"message": "Welcome to FamilyVideoStream!"}

@app.get("/media/list")
async def get_video_list():
    files = []
    for filename in os.listdir(VIDEO_FOLDER):
        if filename.lower().endswith((".mp4", ".mov", ".mkv", ".webm")):
            files.append({
                "title": filename.rsplit('.', 1)[0],  # Remove extension for title
                "filename": filename,
                "thumbnail": f"https://via.placeholder.com/300x169?text={filename.rsplit('.',1)[0]}"
            })
    return files

@app.get("/stream/{filename}")
async def stream_video(filename: str):
    video_path = os.path.join(VIDEO_FOLDER, filename)
    if os.path.exists(video_path):
        return FileResponse(video_path, media_type="video/mp4")
    return {"error": "File not found"}
