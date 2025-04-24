from ultralytics import YOLO
import cv2
import numpy as np
import torch
import json

# test = np.array([[1, 2, 3], 
#  [5, 6, 7], 
#  [9, 10, 11]])

# print(test[:,-1])

# model = YOLO("runs/detect/train15/weights/best.pt")

# results = model('img/subsidi.jpg')


# for result in results:
#     for i,box in enumerate(result.boxes):
#         print(i,box.xyxy[0])
#         print(box.cls.item())

    # boxes = result.boxes  # Boxes object for bounding box outputs
    # masks = result.masks  # Masks object for segmentation masks outputs
    # keypoints = result.keypoints  # Keypoints object for pose outputs
    # probs = result.probs  # Probs object for classification outputs
    # obb = result.obb  # Oriented boxes object for OBB outputs
    # result.show()  # display to screen
    # print(list(result.names.values()))
    # # result.save(filename="result.jpg")  # save to disk
    # print (boxes.xyxy[0])
    # print(result.boxes.cls)
    # # print(int(result.boxes.cls))
    

import glob

files = glob.glob("*.json")

print(type(files))