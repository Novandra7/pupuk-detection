from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from class_predict import Predict
from database import Database
import scheduler

import os

# RUN API
# uvicorn main:app --port 5050 --workers 4

CCTV_CHANNELS = {i["source_name"]: i["url_streaming"] for i in Database().read_cctv_sources()}

predict_instances = {}

class Data(BaseModel):
    sumber_id: int
    shift_id: int
    bag: int
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

@app.get("/read_records/{id}")
def read(id:int):
    return Database().read_records(id)

@app.get("/read_formatted_records/{id}")
def read(id:int):
    return Database().read_formatted_records(id)

@app.get("/read_curdate_records/{id}")
def read(id:int):
    return Database().read_curdate_records(id)

@app.get("/read_cctv_sources")
def read():
    return Database().read_cctv_sources()

@app.get("/read_cctv_sources/{id}")
def read_cctv_sources_by_id(id: int):
    return Database().read_cctv_sources_by_warehouse_id(id)

@app.get("/read_warehouse")
def read():
    return Database().read_warehouse()

@app.get("/read_shift")
def read():
    return Database().read_shift()

@app.get("/write_records")
def write_records():
    scheduler.store()
    return {"status": "success"}

@app.post("/write")
def write(data: list[Data]):
    db = Database()
    for item in data:
        values = tuple(item.model_dump().values())
        print("[DEBUG] Data yang akan disimpan:", values)
        try:
            db.write_record(values)
        except Exception as e:
            print("[ERROR] Gagal menyimpan ke DB:", e)
            raise HTTPException(status_code=500, detail=str(e))
    return {"message": f"{len(data)} records saved successfully."}

            

@app.get("/video_feed/{channel}")
async def video_feed(channel: str):
    instance = predict_instances.get(channel)
    if not instance:
        raise HTTPException(status_code=404, detail="Prediksi belum dimulai untuk channel ini")

    return StreamingResponse(
        instance.stream_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"}
    )
    
@app.get("/start_predict/{channel}")
async def start_predict(channel: str):
    if channel not in CCTV_CHANNELS:
        raise HTTPException(status_code=404, detail="Channel not found")

    if channel in predict_instances:
        return {"message": f"Prediksi untuk channel '{channel}' sudah berjalan."}

    source_id = list(CCTV_CHANNELS.keys()).index(channel) + 1
    instance = Predict(CCTV_CHANNELS[channel], channel, source_id)
    predict_instances[channel] = instance

    return {"message": f"Prediksi dimulai untuk channel '{channel}'"}