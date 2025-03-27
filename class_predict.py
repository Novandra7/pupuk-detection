from ultralytics import YOLO
from sort import Sort
import numpy as np
import json
import cv2
import time

class Predict:
    def __init__(self,source:str):
        self.model = YOLO("runs/detect/train15/weights/best.pt")
        self.tracker = Sort(max_age=120, min_hits=10, iou_threshold=0.5)
        self.cap = cv2.VideoCapture(source)
        self.counted_ids = set()
        self.label = self.read_data()
        self.middle_line = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2  
    
    def read_data(self):
        with open("pupuk_counter.json", "r") as file:
           return json.load(file)
    
    def write_data(self, data:dict):
        with open("pupuk_counter.json", "w") as file:
            json.dump(data, file)         

    def predict(self):
        while True:
            success, frame = self.cap.read()

            if not success:
                break

            start_time = time.time()
    
            results = self.model(frame)
            
            # Siapkan array deteksi untuk SORT
            detections = np.empty((0, 6))

            # Gambar garis tengah
            cv2.line(frame, (self.middle_line, 0), (self.middle_line, frame.shape[0]), (255, 255, 255), 2)
            
            for result in results:
                boxes = result.boxes
                for box in boxes:
                    x_min, y_min, x_max, y_max = map(int, box.xyxy[0])
                    confidence = float(box.conf[0])
                    class_index = int(box.cls[0].item())

                    detection = np.array([x_min, y_min, x_max, y_max, confidence, class_index])
                    detections = np.vstack((detections, detection))
            
            # Update tracker dengan deteksi baru
            tracks = self.tracker.update(detections[:, :-1])
            print(tracks)
            print(detections[:, -1])
            
            # Proses hasil tracking
            for track, class_index in zip(tracks, detections[:, -1]):
                x1, y1, x2, y2, track_id = track
                track_id = int(track_id)
                class_index = int(class_index)
                class_names = list(self.label.keys())  # Ambil urutan nama kelas dari JSON
                detected_class = class_names[class_index]

                # Gambar bounding box dengan label
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                cv2.putText(frame, f"Type: {detected_class}", (int(x1), int(y1) - 10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                
                # Object center
                center_x = (x1 + x2) / 2
                
                # Visualisasi titik tengah objek
                cv2.circle(frame, (int(center_x), int((y1 + y2) / 2)), 4, (0, 255, 255), -1)
                
                if track_id not in self.counted_ids and center_x < self.middle_line :
                        self.label[detected_class] += 1
                        self.write_data(self.label)
                        self.counted_ids.add(track_id)
                        # Highlight objek yang dihitung
                        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 165, 255), 3)
            
            cv2.putText(frame, f"Granul Count: {self.label['granul']}", (90, 120), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (0, 165, 255), 2)
            
            cv2.putText(frame, f"Subsidi Count: {self.label['subsidi']}", (90, 160), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (0, 165, 255), 2)
            
            cv2.putText(frame, f"Prill Count: {self.label['prill']}", (90, 200), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (0, 165, 255), 2)
      
            cv2.putText(frame, f"Bag Count: {self.label['bag']}", (90, 240), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (0, 165, 255), 2)
            
            inference_time = f"Inference Time: {round((time.time() - start_time) * 1000, 2)} ms"

            cv2.putText(frame, inference_time, (90, 280), cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, (0, 165, 255), 2)
            
            # cv2.imshow("cctv", frame)
      
            # if cv2.waitKey(1) & 0xFF == 27:
            #     break
            
            _, buffer = cv2.imencode(".jpg", frame)
            frame_bytes = buffer.tobytes()

            # Streaming frame sebagai response
            yield (b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" + frame_bytes + b"\r\n")

        
        self.cap.release()
        cv2.destroyAllWindows()

# source = [
#     "pupuk.mp4", #0
#     "C:/Users/ASUS/AppData/Local/CapCut/Videos/subsidi-dan-granul.mp4", #1
#     "rtsp://vendor:Bontangpkt2025@36.37.123.10:554/Streaming/Channels/101/", #2
#     "rtsp://pkl:futureisours2025@36.37.123.19:554/Streaming/Channels/101/" #3
#     ]
        
# model = Predict(source[0])
# model.predict()  
# print(model.label) #  12 granul, 8 subsidi  