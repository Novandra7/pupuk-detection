import os
import json
import cv2
import time
import numpy as np
from ultralytics import YOLO
from sort import Sort
from threading import Thread

class Predict:
    def __init__(self, url_stream: str, source_name: str, source_id: int):
        self.model = YOLO("runs/detect/train15/weights/best.pt")
        self.url_stream = url_stream
        self.source_name = source_name
        self.source_id = source_id
        self.label = self.read_data(source_name)[-1]
        self.class_names = list(self.label.keys())
        self.cap = self.init_capture()
        self.tracker = Sort(max_age=120, min_hits=10, iou_threshold=0.5)
        self.counted_ids = set()
        self.middle_line = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2 

        self.latest_frame = None
        self.pred_thread = Thread(target=self._predict_loop, daemon=True)
        self.pred_thread.start()


    def init_capture(self):
        cap = cv2.VideoCapture(self.url_stream, cv2.CAP_FFMPEG)
        if not cap.isOpened():
            raise RuntimeError(f"[ERROR] Tidak bisa membuka stream dari {self.url_stream}")
        return cap

    def reconnect(self):
        print("[INFO] Mencoba reconnect ke stream...")
        self.cap.release()
        time.sleep(1)
        self.cap = self.init_capture()

    def read_data(self, name: str):
        filename = f"pupuk_counter_{name}.json"
        try:
            if os.path.exists(filename) and os.path.getsize(filename) > 0:
                with open(filename, "r") as file:
                    return json.load(file)
            else:
                raise FileNotFoundError  # Perlakukan file kosong sama seperti tidak ditemukan

        except (FileNotFoundError, json.JSONDecodeError):
            default_data = [{
                "sumber_id": self.source_id,
                "bag": 0,
                "granul": 0,
                "subsidi": 0,
                "prill": 0,
                "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
            }]
            with open(filename, "w") as file:
                json.dump(default_data, file, indent=4)
            return default_data
        
    def get_last_data(self, name: str):
        filename = f"pupuk_counter_{name}.json"
        try:
            with open(filename, "r") as file:
                data = json.load(file)
                return data[-1] if isinstance(data, list) else data
        except FileNotFoundError:
            return None

    def write_data(self, data: dict, name: str):
        existing_data = self.read_data(name)
        if not isinstance(existing_data, list):
                existing_data = [existing_data]
        existing_data.append(data)
        with open(f"pupuk_counter_{name}.json", "w") as file:
            json.dump(existing_data, file, indent=4)

    def draw_text(self, frame, text, position, font=cv2.FONT_HERSHEY_SIMPLEX, font_scale=0.7, color=(0, 165, 255), thickness=2):
        return cv2.putText(frame, text, position, font, font_scale, color, thickness)
    
    def stream_frames(self):
        while True:
            if self.latest_frame:
                yield (b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + self.latest_frame + b"\r\n")
            time.sleep(0.03)  # atur delay sesuai kebutuhan (sekitar 30 FPS)

    def _predict_loop(self):
        while True:
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
                    class_index = int(class_index)
                    detected_class = self.class_names[class_index + 1]

                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    self.draw_text(frame, f"Type: {detected_class}", (int(x1), int(y1) - 10), font_scale=0.5, color=(0, 255, 0))

                    center_x = (x1 + x2) / 2
                    cv2.circle(frame, (int(center_x), int((y1 + y2) / 2)), 4, (0, 255, 255), -1)

                    if track_id not in self.counted_ids and center_x < self.middle_line:
                        self.label[detected_class] += 1
                        self.label['sumber_id'] = self.source_id
                        self.label['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S')
                        self.write_data(self.label, self.source_name)
                        self.counted_ids.add(track_id)
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 165, 255), 3)

                self.draw_text(frame, f"Granul Count: {self.label['granul']}", (90, 120))
                self.draw_text(frame, f"Subsidi Count: {self.label['subsidi']}", (90, 160))
                self.draw_text(frame, f"Prill Count: {self.label['prill']}", (90, 200))
                self.draw_text(frame, f"Bag Count: {self.label['bag']}", (90, 240))
                inference_time = f"Inference Time: {round((time.time() - start_time) * 1000, 2)} ms"
                self.draw_text(frame, inference_time, (90, 280))

                # cv2.imshow("cctv", frame)
      
                # if cv2.waitKey(1) & 0xFF == 27:
                #     break

                _, buffer = cv2.imencode(".jpg", frame)
                self.latest_frame = buffer.tobytes()
                
            except GeneratorExit:
                print("[INFO] Stream ditutup oleh client.")
            # except Exception as e:
            #     print(f"[ERROR] Terjadi kesalahan: {e}")
