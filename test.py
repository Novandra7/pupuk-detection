# import cv2

# # URL RTSP stream
# rtsp_url = 'rtsp://vendor:Bontangpkt2025@36.37.123.10:554/Streaming/Channels/101/'

# # Buka stream RTSP
# cap = cv2.VideoCapture(rtsp_url)

# # Periksa apakah stream berhasil dibuka
# if not cap.isOpened():
#     print("Error: Tidak dapat membuka stream RTSP.")
#     exit()

# while True:
#     try:
#         # Baca frame dari stream
#         ret, frame = cap.read()
        
#         # Jika frame berhasil dibaca
#         if not ret:
#             print("Gagal membaca frame.")
#             break
        
#         # Tampilkan frame
#         cv2.imshow('RTSP Stream', frame)
        
#         # Tunggu tombol 'q' untuk keluar
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break
#     except Exception as e:
#         print("error.",e)
#         break

# # Lepaskan objek video dan tutup jendela
# cap.release()
# cv2.destroyAllWindows()

# from class_predict import Predict
# test = Predict("pupuk.mp4", "CCTV-3", 3)
# print(test.label)
# print(test.class_names)
# print(test.get_last_data("CCTV-3"))

print("berhasil menjalankan docker")