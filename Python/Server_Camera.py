import time
import cv2
import urllib.request
import numpy as np
import os
import mysql.connector
from fer import FER
from PIL import Image
from ESP32 import *
import Server
import mediapipe as mp

# Khởi tạo bộ nhận diện khuôn mặt
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
emotion_detector = FER()

url = 'http://192.168.226.72/cam-lo.jpg'

# Đường dẫn thư mục để lưu ảnh
output_folder  = r'D:\IOT\openWithFace\openWithFace\Python\image'

db_config = {
    'user': 'root',
    'password': '123456',
    'host': 'localhost',
    'database': 'face_recognition',
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

while True:
    # Biến cờ để kiểm tra xem đã chụp ảnh hay chưa
    capture_flag = False
    img = urllib.request.urlopen(url)
    img_np = np.array(bytearray(img.read()), dtype=np.uint8)
    frame = cv2.imdecode(img_np, -1)

    frame = cv2.flip(frame, 0)

    # Kiểm tra xem frame có rỗng không
    if frame is None or frame.size == 0:
        print("Error: Frame is empty, skipping this iteration.")
        time.sleep(1)  # Đợi một chút trước khi thử lại
        continue  # Bỏ qua vòng lặp này


    # Nhận diện khuôn mặt trong ảnh
    faces = face_cascade.detectMultiScale(frame, scaleFactor=1.3, minNeighbors=5)

    # Vẽ hình chữ nhật xung quanh khuôn mặt và chụp ảnh tự động
    for (x, y, w, h) in faces:
        # Chụp toàn bộ mặt khi có khuôn mặt được nhận diện và biến cờ là True
        if not capture_flag:
            face_roi = frame[y:y + h, x:x + w]
            img_path = os.path.join(output_folder, 'captured_face.jpg')
            cv2.imwrite(img_path, frame)  # Chụp toàn bộ khung chứa khuôn mặt
            capture_flag = True  # Dừng vòng lặp sau khi chụp ảnh

            # Perform emotion detection
            image = Image.open(img_path)
            emotion, score = emotion_detector.top_emotion(np.array(image))
            print(f"Detected emotion: {emotion} with score: {score}")

    cv2.imshow('img', frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

    if capture_flag == True:
        image_path = 'D:\IOT\openWithFace\openWithFace\Python\image\captured_face.jpg'
        image = Image.open(image_path)

        # Convert the image to a numpy array
        image_np = np.array(image)

        # Process the image using the existing function
        name = Server.process(image_np)
        print(name)
        time.sleep(2)

# Dòng này đảm bảo rằng cửa sổ hiển thị được đóng khi thoát khỏi vòng lặp
cv2.destroyAllWindows()