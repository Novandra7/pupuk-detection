import os
import cv2
import time
import json
import logging
import numpy as np
from threading import Thread
from ultralytics import YOLO
from datetime import datetime
from sort import Sort
from database import Database

logging.basicConfig(
    filename=f"{time.strftime('%Y-%m-%d')}.txt",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

from threading import Thread
from sql_server import Database
from datetime import datetime

class Predict:
    def __init__(self, url_stream: str, cctv_name: str, id_cctv: int):
        self.url_stream = url_stream
        self.cctv_name = cctv_name
        self.id_cctv = id_cctv

        self.cap = self.init_capture()
        self.model = YOLO("./runs/detect/train15/weights/best.pt")
        self.tracker = Sort(max_age=120, min_hits=10, iou_threshold=0.5)

        self.label = Database().read_bag()
        self.shift = Database().read_shift()
        self.temp_data_format = dict.fromkeys(Database().read_temp_data_format())

        self.counted_ids = set()
        self.total_qty = {}
        self.middle_line = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2

        self.latest_frame = None
        self.is_running = True

        self.pred_thread = Thread(target=self._predict_loop, daemon=True)
        self.pred_thread.start()

    def init_capture(self):
        cap = cv2.VideoCapture(self.url_stream, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            logging.warning(f"Gagal membuka stream: {self.url_stream}")
            return None
        logging.info(f"Stream berhasil dibuka: {self.url_stream}")
        return cap


    def reconnect(self):
        logging.warning(f"Stream {self.cctv_name} mati. Mencoba reconnect...")
        if self.cap:
            self.cap.release()
        time.sleep(1)
        while True:
            try:
                print("reconnect")
                self.cap = self.init_capture()
                if self.cap.isOpened():
                    logging.info(f"Reconnect berhasil untuk {self.cctv_name}")
                    break
            except Exception as e:
                logging.warning(f"Gagal reconnect {self.cctv_name}: {e}")
            time.sleep(5)

    def write_data(self, data: list, name: str):
        filename = f"pupuk_counter_{name}.json"

        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, "r") as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        new_data = dict(zip(self.temp_data_format.keys(), data))
        existing_data.append(new_data)

        with open(filename, "w") as file:
            json.dump(existing_data, file, indent=4)

    def draw_text(self, frame, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.7, color=(0, 165, 255), thickness=2):
        return cv2.putText(frame, text, position, font, font_scale, color, thickness)

    def detect_current_shift(self, current_time_str):
        current_time = datetime.strptime(current_time_str, "%H:%M:%S").time()
        for shift in self.shift:
            start = datetime.strptime(shift["start_time"], "%H:%M:%S").time()
            end = datetime.strptime(shift["end_time"], "%H:%M:%S").time()
            if start > end:  # shift malam
                if current_time >= start or current_time <= end:
                    return shift["id"]
            else:
                if start <= current_time <= end:
                    return shift["id"]
        return None

    def stream_frames(self):
        while self.is_running:
            if self.latest_frame:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + self.latest_frame + b"\r\n")
            time.sleep(0.03)

    def _predict_loop(self):
        logging.info(f"Memulai prediksi untuk {self.cctv_name}")
        while self.is_running:
            try:
                success, frame = self.cap.read()
                if not success or frame is None:
                    logging.warning(f"Frame gagal dibaca dari {self.cctv_name}, mencoba reconnect...")
                    self.reconnect()
                    continue

                start_time = time.time()
                results = self.model(frame)
                detections = np.empty((0, 6))
                cv2.line(frame, (self.middle_line, 0), (self.middle_line, frame.shape[0]), (255, 255, 255), 2)

                for result in results:
                    for box in result.boxes:
                        x_min, y_min, x_max, y_max = map(int, box.xyxy[0])
                        confidence = float(box.conf[0])
                        class_index = int(box.cls[0].item())
                        detection = np.array([x_min, y_min, x_max, y_max, confidence, class_index])
                        detections = np.vstack((detections, detection))

                tracks = self.tracker.update(detections[:, :-1])

                for track, class_index in zip(tracks, detections[:, -1]):
                    x1, y1, x2, y2, track_id = track
                    track_id = int(track_id)
                    class_index = int(class_index) + 1
                    detected_class = self.label[class_index]
                    detected_class_id = detected_class['id']
                    detected_class_bag_type = detected_class['bag_type']

                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    self.draw_text(frame, f"Type: {detected_class_bag_type}", (int(x1), int(y1) - 10), font_scale=0.5)

                    center_x = (x1 + x2) / 2

                    if track_id not in self.counted_ids and center_x < self.middle_line:
                        current_shift_time = time.strftime('%H:%M:%S')
                        shift_id = self.detect_current_shift(current_shift_time)

                        if detected_class_id not in self.total_qty:
                            self.total_qty[detected_class_id] = 1
                        else:
                            self.total_qty[detected_class_id] += 1

                        data = [self.id_cctv, shift_id, detected_class_id, 1, time.strftime('%Y-%m-%d %H:%M:%S')]
                        self.temp_data_format.update(dict(zip(self.temp_data_format.keys(), data)))
                        self.write_data(data, self.cctv_name)
                        self.counted_ids.add(track_id)

                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 165, 255), 3)

                y_pos = 100
                for class_id, total in self.total_qty.items():
                    class_name = next((v["bag_type"] for v in self.label if v["id"] == class_id), f"ID {class_id}")
                    self.draw_text(frame, f"{class_name} Count: {total}", (90, y_pos))
                    y_pos += 30

                inference_time = f"Inference Time: {round((time.time() - start_time) * 1000, 2)} ms"
                self.draw_text(frame, inference_time, (90, 280))

                # cv2.imshow("cctv", frame)
      
                # if cv2.waitKey(1) & 0xFF == 27:
                #     break

                # Validasi frame sebelum encode
                if frame is not None and frame.size > 0:
                    _, buffer = cv2.imencode(".jpg", frame)
                    self.latest_frame = buffer.tobytes()

            except GeneratorExit:
                logging.info(f"Stream ditutup oleh client untuk {self.cctv_name}")
            except Exception as e:
                logging.error(f"Terjadi kesalahan: {e}")
                self.reconnect()
                time.sleep(1)

    def stop_predict(self):
        logging.info(f"Prediksi dihentikan untuk {self.cctv_name}")
        self.is_running = False
        self.latest_frame = None
        self.cap.release()

# Predict("pupuk.mp4", "CCTV-2", 2)._predict_loop()
