import json
import time
import schedule
import requests
from pathlib import Path
from datetime import datetime

class Scheduler:
    def __init__(self):
        self.url = "http://127.0.0.1:5050/write"
        self.filenames = Path('.').glob('*.json') 
        self.running = False

    def read_data(self,filename):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            print("[ERROR] File JSON tidak ditemukan!")
            return {}  # Mengembalikan dictionary kosong jika file tidak ditemukan
        except json.JSONDecodeError:
            print("[ERROR] File JSON rusak atau tidak valid!")
            return {}  # Mengembalikan dictionary kosong jika JSON tidak valid

    def store(self):
        for file in self.filenames:
            print(f"[{datetime.now()}] Memproses file: {file.name}")
            data = self.read_data(file)
            for i in data:
                print(i['timestamp'])

            if not data:
                print(f"[WARNING] Data kosong di file {file.name}, lewati.")
                continue
            
            try:
                response = requests.post(self.url, json=data, timeout=3)  # Tambahkan timeout 3 detik
                response.raise_for_status()  # Mendeteksi error HTTP (4xx atau 5xx)

                print("[SUCCESS] Data berhasil dikirim:")

                file.unlink()
                print(f"[INFO] File {file.name} telah dihapus setelah berhasil dikirim.")

            except requests.exceptions.RequestException as e:
                print(f"[ERROR] Gagal mengirim request: {e}")

    def run_scheduler(self):
        schedule.every(10).minutes.do(self.store)
        print("[INFO] scheduler dimulai")
        self.running = True
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                print("\n[INFO] Program dihentikan oleh pengguna.")
                break
            
    def stop_scheduler(self):
        self.running = False
        print("[INFO] Scheduler dihentikan secara programatik.")