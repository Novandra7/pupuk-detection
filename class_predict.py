import os
import json
import cv2
import time
import subprocess
import numpy as np
from ultralytics import YOLO
from sort import Sort
from threading import Thread
from database import Database
from datetime import datetime

class Predict:
    def __init__(self, url_stream: str, cctv_name: str, id_cctv: int):
        self.url_stream = url_stream
        self.cap = self.init_capture()
        self.tracker = Sort(max_age=120, min_hits=10, iou_threshold=0.5)
        self.counted_ids = set()
        self.middle_line = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2 

        self.model = YOLO("./runs/detect/train15/weights/best.pt")
        self.cctv_name = cctv_name
        self.id_cctv = id_cctv
        self.label = Database().read_bag()
        self.shift = Database().read_shift()
        self.temp_data_format = dict.fromkeys(Database().read_temp_data_format())
        self.total_qty = {}
        self.is_running = True
    
        self.latest_frame = None
        self.pred_thread = Thread(target=self._predict_loop, daemon=True)
        self.pred_thread.start()

    def init_capture(self):
        # def is_rtsp_accessible(url, timeout=5):
        #     try:
        #         subprocess.run(
        #             ["ffprobe", "-v", "error", "-rtsp_transport", "tcp", "-i", url],
        #             stdout=subprocess.DEVNULL,
        #             stderr=subprocess.DEVNULL,
        #             timeout=timeout
        #         )
        #         return True
        #     except subprocess.TimeoutExpired:
        #         print(f"[ERROR] RTSP check timeout setelah {timeout} detik")
        #         return False
        #     except Exception as e:
        #         print(f"[ERROR] RTSP tidak dapat diakses: {e}")
        #         return False

        # if not is_rtsp_accessible(self.url_stream):
        #     raise RuntimeError(f"[ERROR] Tidak bisa mengakses stream RTSP: {self.url_stream}")

        cap = cv2.VideoCapture(self.url_stream, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            raise RuntimeError(f"[ERROR] Gagal membuka stream setelah ffprobe sukses: {self.url_stream}")
        
        return cap


    def reconnect(self):
        print("[INFO] Mencoba reconnect ke stream...")
        self.cap.release()
        time.sleep(1)
        self.cap = self.init_capture()


    def write_data(self, data: list, name: str):
        filename = f"pupuk_counter_{name}.json"
        
        # Baca data lama
        if os.path.exists(filename) and os.path.getsize(filename) > 0:
            with open(filename, "r") as file:
                try:
                    existing_data = json.load(file)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # Bungkus list data menjadi dictionary pakai kunci dari self.temp_data_format
        new_data = dict(zip(self.temp_data_format.keys(), data))

        existing_data.append(new_data)

        with open(filename, "w") as file:
            json.dump(existing_data, file, indent=4)


    def draw_text(self, frame, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.7, color=(0, 165, 255), thickness=2):
        return cv2.putText(frame, text, position, font, font_scale, color, thickness)
    
    def stream_frames(self):
        while self.is_running:
            if self.latest_frame:
                yield (b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + self.latest_frame + b"\r\n")
            time.sleep(0.03)  # atur delay sesuai kebutuhan (sekitar 30 FPS)
    
    def detect_current_shift(self, current_time_str):
        current_time = datetime.strptime(current_time_str, "%H:%M:%S").time()
        
        for shift in self.shift:
            start = datetime.strptime(shift["start_time"], "%H:%M:%S").time()
            end = datetime.strptime(shift["end_time"], "%H:%M:%S").time()
            
            # Shift malam yang melewati tengah malam
            if start > end:
                if current_time >= start or current_time <= end:
                    return shift["id"]
            else:
                if start <= current_time <= end:
                    return shift["id"]
        
        return None

    def _predict_loop(self):
        print(f"[INFO] prediksi dimulai untuk {self.cctv_name}")
        while self.is_running:
            try:
                success, frame = self.cap.read()

                if not success:
                    self.reconnect()
                    continue

                start_time = time.time()
                results = self.model(frame)
                detections = np.empty((0, 6))
                cv2.line(frame, (self.middle_line, 0), (self.middle_line, frame.shape[0]), (255, 255, 255), 2)

                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        x_min, y_min, x_max, y_max = map(int, box.xyxy[0])
                        confidence = float(box.conf[0])
                        class_index = int(box.cls[0].item())
                        detection = np.array([x_min, y_min, x_max, y_max, confidence, class_index])
                        detections = np.vstack((detections, detection))

                tracks = self.tracker.update(detections[:, :-1])

                for track, class_index in zip(tracks, detections[:, -1]):
                    x1, y1, x2, y2, track_id = track
                    track_id = int(track_id)
                    class_index = int(class_index) + 1  # skip 1 untuk class undefined
                    detected_class = self.label[class_index]
                    detected_class_id = detected_class['id']
                    detected_class_bag_type = detected_class['bag_type']

                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    self.draw_text(frame, f"Type: {detected_class_bag_type}", (int(x1), int(y1) - 10), font_scale=0.5, color=(0, 255, 0))

                    center_x = (x1 + x2) / 2
                    cv2.circle(frame, (int(center_x), int((y1 + y2) / 2)), 4, (0, 255, 255), -1)

                    if track_id not in self.counted_ids and center_x < self.middle_line:
                        current_shift_time = time.strftime('%H:%M:%S')
                        detect_current_shift = self.detect_current_shift(current_shift_time)

                        if detected_class_id not in self.total_qty:
                            self.total_qty[detected_class_id] = 1
                        else:
                            self.total_qty[detected_class_id] += 1

                        data = [self.id_cctv, detect_current_shift, detected_class_id, 1, time.strftime('%Y-%m-%d %H:%M:%S')]
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

                _, buffer = cv2.imencode(".jpg", frame)
                self.latest_frame = buffer.tobytes()
                
            except GeneratorExit:
                print("[INFO] Stream ditutup oleh client.")
            except Exception as e:
                print(f"[ERROR] Terjadi kesalahan: {e}")
                self.reconnect()
                time.sleep(1)

    def stop_predict(self):
        print(f"[INFO] prediksi dihentikan untuk {self.cctv_name}")
        self.is_running = False
        self.latest_frame = None
        self.cap.release()


# Predict("pupuk.mp4", "CCTV-2", 2)._predict_loop()
# Predict("rtsp://vendor:Bontangpkt2025@36.37.123.10:554/Streaming/Channels/101/", "CCTV-2", 2)._predict_loop()

