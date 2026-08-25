from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
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
    try:
        # ប្រើប្រាស់ TikWM API សម្រាប់ទាញយកវីដេអូ TikTok យ៉ាងរលូន
        api_url = f"https://www.tikwm.com/api/?url={data.url}"
        response = requests.get(api_url)
        res_data = response.json()
        
        if res_data.get("code") == 0:
            video_info = res_data.get("data", {})
            # เอาลิงก์ดาวน์โหลดแบบ HD หรือแบบธรรมดา
            download_url = video_info.get("hdplay") or video_info.get("play")
            title = video_info.get("title", "TikTok Video")
            
            if not download_url:
                raise Exception("រកមិនឃើញ Link សម្រាប់ Download ទេ")
                
            return {
                "title": title,
                "thumbnail": video_info.get("cover", ""),
                "download_url": download_url
            }
        else:
            raise Exception("Link នេះមិនត្រឹមត្រូវ ឬមិនអាចទាញយកបានទេ")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
