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
        # ប្រើប្រាស់ Cobalt API (Tool ទាញយកវីដេអូឥតគិតថ្លៃ និងលឿនបំផុត)
        api_url = "https://co.wuk.sh/api/json"
        payload = {
            "url": data.url,
            "vQuality": "max"
        }
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        res_data = response.json()
        
        if res_data.get("status") == "redirect" or res_data.get("status") == "stream":
            download_url = res_data.get("url")
            return {
                "title": "Downloaded Video",
                "thumbnail": "",
                "download_url": download_url
            }
        elif res_data.get("status") == "picker":
            # ករណីมีหลายไฟล์ (เช่น รูปภาพหลายรูป) យកอันដំបូង
            download_url = res_data.get("picker")[0].get("url")
            return {
                "title": "Downloaded Video",
                "thumbnail": "",
                "download_url": download_url
            }
        else:
            raise Exception(res_data.get("text", "មិនអាចទាញយក Link ນີ້បានទេ"))
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
