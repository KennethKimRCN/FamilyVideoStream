# FamilyVideoStream

FamilyVideoStream is a custom-built video streaming server designed for personal and family use. It allows smooth playback of 4K HEVC videos, complete with metadata, thumbnail previews, favorite tagging, and more.

## Features

- Stream 4K HEVC videos with support for up to 5 concurrent users
- FastAPI backend for serving video, preview, and thumbnail data
- Netflix-style UI built with HTML, CSS, and JavaScript
- Keyboard shortcuts for video control (Esc, Space, Arrow keys, Fullscreen)
- External progress bar with hover preview (scrub thumbnails)
- Real-time metadata display including codec, duration, resolution
- Drag-and-drop video uploads (admin use)
- Favorite tagging system (saved in browser)
- Search and filter videos by title or favorites

## Tech Stack

- Python 3.10+
- FastAPI
- FFmpeg (must be in system PATH)
- HTML/CSS/JavaScript frontend (single-page app)
- Optional: Nginx for reverse proxy or HTTPS

## Installation

1. Clone this repository:

```bash
git clone https://github.com/KennethKimRCN/FamilyVideoStream.git
cd FamilyVideoStream
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Ensure `ffmpeg` and `ffprobe` are installed and accessible from PATH.

4. Run the FastAPI app:

```bash
uvicorn main:app --reload
```

5. Open your browser and visit:

```
http://localhost:8000
```

## Folder Structure

```
FamilyVideoStream/
├── main.py             # FastAPI app
├── utils.py            # Thumbnail & metadata utilities
├── templates/
│   └── index.html      # Web frontend
├── static/
│   └── ...             # (if used for CSS/JS assets)
├── videos/             # Your video files
├── thumbnails/         # Auto-generated thumbnails
├── previews/           # Short hover previews
├── sprites/            # Timeline sprite images
├── ffmpeg.log          # Logs from FFmpeg
```

## Uploading Videos

- Drag and drop video files directly into the webpage.
- Files are uploaded to the server and automatically processed for preview and metadata.

## TODO

- Admin authentication for upload/delete
- HLS adaptive bitrate streaming support
- Database-backed metadata and favorites (future upgrade)
- Support mobile layout optimizations

## License

MIT License
