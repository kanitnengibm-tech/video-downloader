from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

# អនុញ្ញាតឱ្យ Browser អាចតភ្ជាប់មកកាន់ Backend បាន
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class VideoRequest(BaseModel):
    url: str

@app.post("/api/extract")
def extract_video(data: VideoRequest):
    ydl_opts = {
        'format': 'best',
        'quiet': True,
        'no_warnings': True,
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # ទាញយកទិន្នន័យវីដេអូដោយមិនបាច់ទាញយកហ្វាលទាំងមូលមកកុំព្យូទ័រ
            info = ydl.extract_info(data.url, download=False)
            
            # ទាញយក Link វីដេអូដើមផ្ទាល់
            video_url = info.get('url')
            if not video_url and 'entries' in info:
                video_url = info['entries'][0].get('url')
            
            return {
                "title": info.get('title', 'វីដេអូគ្មានចំណងជើង'),
                "thumbnail": info.get('thumbnail'),
                "download_url": video_url
            }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))