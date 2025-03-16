from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from class_predict import Predict
from database import Database


import cv2

# cap = cv2.VideoCapture("pupuk.mp4")


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
            
@app.get("/video_feed")
async def video_feed():
    try:
        return StreamingResponse(Predict("pupuk.mp4").predict(), media_type="multipart/x-mixed-replace; boundary=frame")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
