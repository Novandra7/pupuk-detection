import json
import time
import schedule
import requests
import logging
from pathlib import Path
from datetime import datetime

# Konfigurasi logging
logging.basicConfig(
    level=logging.INFO,
    format="[{asctime}] {levelname}: {message}",
    style="{",
    handlers=[
        logging.FileHandler("scheduler.log"),  # log ke file
        logging.StreamHandler()                # log ke console
    ]
)

class Scheduler:
    def __init__(self):
        self.url = "http://12.7.25.82:5050/write"
        self.running = True

    def read_data(self, filename):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
            return data
        except FileNotFoundError:
            logging.error("File JSON tidak ditemukan!")
            return {}
        except json.JSONDecodeError:
            logging.error("File JSON rusak atau tidak valid!")
            return {}

    def store(self):
        for file in Path('.').glob('*.json'):
            logging.info(f"Memproses file: {file.name}")
            data = self.read_data(file)

            if not data:
                logging.warning(f"Data kosong di file {file.name}, lewati.")
                continue
            
            try:
                response = requests.post(self.url, json=data)
                response.raise_for_status()

                logging.info(f"Data berhasil dikirim dari file: {file.name}")
                file.unlink()
                logging.info(f"File {file.name} telah dihapus setelah berhasil dikirim.")
            except requests.exceptions.RequestException as e:
                logging.error(f"Gagal mengirim request: {e}")

    def run_scheduler(self):
        job = schedule.every(10).minutes.do(self.store)
        logging.info("Scheduler dimulai")
        logging.info(f"Job terjadwal: {job}")
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                logging.info("Program dihentikan oleh pengguna.")
                break

    def stop_scheduler(self):
        self.running = False
        logging.info("Scheduler dihentikan secara programatik.")
