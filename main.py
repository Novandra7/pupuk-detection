from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel
from class_predict import Predict
from database import Database
from typing import Optional

from scheduler import Scheduler
import threading

# RUN API
# uvicorn {file_name}:{ variable_class_FastAPI } --port 5050

app = FastAPI()

CCTV_CHANNELS = {i["source_name"]: i["url_streaming"] for i in Database().read_cctv_sources()}
predict_instances = {}
scheduler_instance = Scheduler()

class Data(BaseModel):
    ms_cctv_sources_id: int
    ms_shift_id: int
    ms_bag_id: int
    quantity: int
    timestamp: str


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
def read(id: int, date: Optional[str] = Query(None), name: Optional[str] = Query(None), shift:Optional[str] = Query(None)):
    return Database().read_formatted_records(id, date, name, shift)

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
def write():
    scheduler_instance.store()
    return{"message": "Berhasil store data."}


@app.get("/start_scheduler")
def start_scheduler():
    if scheduler_instance.running:
        return {"message": "Scheduler sudah berjalan."}

    scheduler_thread = threading.Thread(target=scheduler_instance.run_scheduler, daemon=True)
    scheduler_thread.start()
    return {"message": "Scheduler dimulai."}   

@app.get("/stop_scheduler")
def stop_scheduler():
    if not scheduler_instance.running:
        return {"message": "Scheduler belum berjalan."}
    scheduler_instance.stop_scheduler()
    return {"message": "Scheduler dihentikan."} 

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
def start_predict(channel: str, background_tasks: BackgroundTasks):
    if channel not in CCTV_CHANNELS:
        raise HTTPException(status_code=404, detail="Channel not found")

    if channel in predict_instances:
        return {"message": f"Prediksi untuk channel '{channel}' sudah berjalan."}

    def run_prediction():
        source_id = list(CCTV_CHANNELS.keys()).index(channel) + 1
        instance = Predict(CCTV_CHANNELS[channel], channel, source_id)
        predict_instances[channel] = instance
        print(f"[INFO] Background prediksi dimulai untuk {channel}")

    background_tasks.add_task(run_prediction)

    return {"message": f"Prediksi untuk '{channel}' dijadwalkan di background."}

@app.get("/stop_predict/{channel}")
async def stop_predict(channel: str, ):
    instance = predict_instances.get(channel)
    if not instance:
        raise HTTPException(status_code=404, detail="Prediksi tidak ditemukan untuk channel ini")
    try:
        instance.stop_predict()
        del predict_instances[channel]
        return {"message": f"Prediksi dihentikan untuk channel '{channel}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gagal menghentikan prediksi: {e}")


@app.post("/write")
def write(data: list[Data]):
    for item in data:
        values = tuple(item.model_dump().values())
        print("[DEBUG] Data yang akan disimpan:", values)
        try:
            Database().write_record(values)
        except Exception as e:
            print("[ERROR] Gagal menyimpan ke DB:", e)
            raise HTTPException(status_code=500, detail=str(e))
    return {"message": f"{len(data)} records saved successfully."}