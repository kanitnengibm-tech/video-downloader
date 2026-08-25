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
        # ប្រើប្រាស់ Cobalt API ស៊េរីថ្មីសម្រាប់គ្រប់ Platform (TikTok, FB, IG, YT...)
        api_url = "https://api.cobalt.tools/api/json"
        payload = {
            "url": data.url,
            "vQuality": "max"
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        res_data = response.json()
        
        status = res_data.get("status")
        
        if status in ["redirect", "stream"]:
            return {
                "title": "Downloaded Video",
                "thumbnail": "",
                "download_url": res_data.get("url")
            }
        elif status == "picker":
            # ករណីមានหลายไฟล์ យកอันแรก
            items = res_data.get("picker", [])
            if items:
                return {
                    "title": "Downloaded Video",
                    "thumbnail": "",
                    "download_url": items[0].get("url")
                }
        
        raise Exception(res_data.get("text", "មិនអាចទាញយក Link นี้ได้ទេ"))
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
