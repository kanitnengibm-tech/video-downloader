from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
import requests
import re
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
    url = data.url.strip()
    
    # 1. ករណីជា TikTok / Douyin
    if "tiktok.com" in url or "douyin.com" in url:
        try:
            res = requests.get(f"https://www.tikwm.com/api/?url={url}", timeout=10).json()
            if res.get("code") == 0:
                d = res.get("data", {})
                return {
                    "title": d.get("title", "TikTok Video"),
                    "thumbnail": d.get("cover", ""),
                    "download_url": d.get("play") or d.get("hdplay")
                }
        except Exception:
            pass

    # 2. ករណីជា Instagram
    elif "instagram.com" in url:
        try:
            api_ig = f"https://api.vkrdownloader.com/server?vkr={url}"
            res = requests.get(api_ig, timeout=10).json()
            data_res = res.get("data", {})
            dl_url = data_res.get("downloadUrl") or (data_res.get("downloads", [{}])[0].get("url") if data_res.get("downloads") else None)
            if dl_url:
                return {
                    "title": "Instagram Video",
                    "thumbnail": data_res.get("thumbnail", ""),
                    "download_url": dl_url
                }
        except Exception:
            pass

    # 3. ករណីជា Facebook ឬ YouTube និង Link ផ្សេងៗ
    try:
        api_general = f"https://api.vkrdownloader.com/server?vkr={url}"
        res = requests.get(api_general, timeout=15).json()
        if res.get("status") == "success" or res.get("data"):
            data_res = res.get("data", {})
            downloads = data_res.get("downloads", [])
            
            dl_url = None
            if downloads:
                dl_url = downloads[0].get("url")
            elif data_res.get("downloadUrl"):
                dl_url = data_res.get("downloadUrl")
                
            if dl_url:
                return {
                    "title": data_res.get("title", "Video"),
                    "thumbnail": data_res.get("thumbnail", ""),
                    "download_url": dl_url
                }
    except Exception:
        pass

    raise HTTPException(status_code=400, detail="មិនអាចទាញយក Link នេះបានទេ! សូមពិនិត្យមើល Link ម្តងទៀត។")
