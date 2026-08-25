from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
import yt_dlp
import os
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

class VideoRequest(BaseModel):
    url: str

def remove_file(path: str):
    try:
        if os.path.exists(path):
            os.remove(path)
    except Exception:
        pass

@app.get("/", response_class=HTMLResponse)
def read_root():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Server is running!</h1>"

@app.post("/api/extract")
def extract_video(data: VideoRequest):
    file_id = str(uuid.uuid4())
    output_template = os.path.join(DOWNLOAD_FOLDER, f"{file_id}.%(ext)s")
    
    # កំណត់ Headers ដើម្បីកុំឱ្យ TikTok បិទស្ទាក់
    ydl_opts = {
        'format': 'best',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=True)
            title = info.get('title', 'Video')
            thumbnail = info.get('thumbnail')
            
            # ស្វែងរកហ្វាលដែលទើបទាញយកបាន
            found_file = None
            for file in os.listdir(DOWNLOAD_FOLDER):
                if file.startswith(file_id):
                    found_file = file
                    break
            
            if not found_file:
                raise Exception("មិនអាចបង្កើត File វីដេអូបានទេ")
                
            return {
                "title": title,
                "thumbnail": thumbnail,
                "file_id": found_file
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/download/{filename}")
def download_file(filename: str, background_tasks: BackgroundTasks):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    background_tasks.add_task(remove_file, file_path)
    
    return FileResponse(
        path=file_path, 
        media_type="application/octet-stream", 
        filename="video.mp4"
    )
