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
    
    ydl_opts = {
        'format': 'best[ext=mp4]/best',
        'outtmpl': output_template,
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=True)
            title = info.get('title', 'video')
            thumbnail = info.get('thumbnail')
            
            # រកមើល file ដែលទើប download បាន
            filename = None
            for file in os.listdir(DOWNLOAD_FOLDER):
                if file.startswith(file_id):
                    filename = file
                    break
            
            if not filename:
                raise Exception("មិនអាចបង្កើត File វីដេអូបានទេ")
                
            return {
                "title": title,
                "thumbnail": thumbnail,
                "file_id": filename
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/download/{filename}")
def download_file(filename: str, background_tasks: BackgroundTasks):
    file_path = os.path.join(DOWNLOAD_FOLDER, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
        
    # លុប file ចេញពី server ក្រោយពេល user download រួច
    background_tasks.add_task(remove_file, file_path)
    
    return FileResponse(
        path=file_path, 
        media_type="video/mp4", 
        filename="video.mp4"
    )
