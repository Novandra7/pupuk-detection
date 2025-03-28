from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from class_predict import Predict
from database import Database

# RUN API
# uvicorn main:app --port 5050 --workers 2

CCTV_CHANNELS = {
    "Kamera1": "rtsp://pkl:futureisours2025@36.37.123.19:554/Streaming/Channels/101/",
    "Kamera2": "rtsp://vendor:Bontangpkt2025@36.37.123.10:554/Streaming/Channels/101/",
    "video": "pupuk.mp4"
}

class Data(BaseModel):
    granul: int
    subsidi: int
    prill: int

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/read")
async def read():
    return Database().read_data()

@app.post("/write")
async def write(data:Data):
    return Database().write_data(tuple(data.model_dump().values()))
            
@app.get("/video_feed/{channel}")
async def video_feed(channel:str):
    if channel not in CCTV_CHANNELS:
        raise HTTPException(status_code=404, detail="Channel not found")
    
    try:
        return StreamingResponse(
            Predict(CCTV_CHANNELS[channel]).predict(),
            media_type="multipart/x-mixed-replace; boundary=frame"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))