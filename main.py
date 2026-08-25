from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, StreamingResponse
from pydantic import BaseModel
import yt_dlp
import requests
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.get("/", response_class=HTMLResponse)
def read_root():
    if os.path.exists("index.html"):
        with open("index.html", "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Server is running!</h1>"

@app.post("/api/extract")
def extract_video(data: VideoRequest):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(data.url, download=False)
            video_url = info.get('url')
            if not video_url and 'entries' in info:
                video_url = info['entries'][0].get('url')
            
            # បង្កើត Link ទាញយកតាមរយៈ Proxy របស់ Server យើងផ្ទាល់
            proxy_download_url = f"/api/download?url={requests.utils.quote(video_url)}"
            
            return {
                "title": info.get('title', 'Video'),
                "thumbnail": info.get('thumbnail'),
                "download_url": proxy_download_url
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# API ជំនួយបញ្ជូន Video Stream ដើម្បីកុំឱ្យជាប់ Error 403
@app.get("/api/download")
def download_stream(url: str):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://www.tiktok.com/'
    }
    
    def iterfile():
        with requests.get(url, headers=headers, stream=True) as r:
            r.raise_for_status()
            for chunk in r.iter_content(chunk_size=8192):
                yield chunk

    return StreamingResponse(
        iterfile(),
        media_type="video/mp4",
        headers={"Content-Disposition": 'attachment; filename="video.mp4"'}
    )
