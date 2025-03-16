import json
import time
import schedule
import requests

def read_data():
    try:
        with open("pupuk_counter.json", "r") as file:
            data = json.load(file)
        data.pop('bag',None)
        return data
    except FileNotFoundError:
        print("[ERROR] File JSON tidak ditemukan!")
        return {}  # Mengembalikan dictionary kosong jika file tidak ditemukan
    except json.JSONDecodeError:
        print("[ERROR] File JSON rusak atau tidak valid!")
        return {}  # Mengembalikan dictionary kosong jika JSON tidak valid

def store():
    url = "http://127.0.0.1:5050/write"
    data = read_data()

    if not data:  
        print("[WARNING] Data kosong, tidak mengirim request.")
        return  # Tidak mengirim request jika data kosong

    try:
        response = requests.post(url, json=data, timeout=2)  # Tambahkan timeout 5 detik
        response.raise_for_status()  # Mendeteksi error HTTP (4xx atau 5xx)

        print("[SUCCESS] Data berhasil dikirim:", data)

    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Gagal mengirim request: {e}")

schedule.every(1).hours.do(store)

while True:
    try:
        schedule.run_pending()
        time.sleep(1)
    except KeyboardInterrupt:
        print("\n[INFO] Program dihentikan oleh pengguna.")
        break
