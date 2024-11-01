import time
import cv2
import urllib.request
import numpy as np
import os

from PIL import Image
import firebase_admin
from firebase_admin import credentials

from ESP32 import *
import Server

# Khởi tạo bộ nhận diện khuôn mặt
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

url = 'http://192.168.0.103/cam-lo.jpg'

# Đường dẫn thư mục để lưu ảnh
output_folder = r'/Users/trantuan/Downloads/Face_Lock_IoT-main/Python/image/'

cred = credentials.Certificate("./serviceAccount.json")
app = firebase_admin.initialize_app(cred, {
    'databaseURL': "https://faceiot-7f1d0-default-rtdb.firebaseio.com/"
    })

while True:
    # Biến cờ để kiểm tra xem đã chụp ảnh hay chưa
    capture_flag = False
    img = urllib.request.urlopen(url)
    img_np = np.array(bytearray(img.read()), dtype=np.uint8)
    frame = cv2.imdecode(img_np, -1)

    # Chuyển ảnh sang đen trắng để tăng tốc độ xử lý
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Nhận diện khuôn mặt trong ảnh
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Vẽ hình chữ nhật xung quanh khuôn mặt và chụp ảnh tự động
    for (x, y, w, h) in faces:

        # Chụp toàn bộ mặt khi có khuôn mặt được nhận diện và biến cờ là True
        if not capture_flag:
            face_roi = frame[y:y + h, x:x + w]
            img_path = os.path.join(output_folder, 'captured_face.jpg')
            cv2.imwrite(img_path, frame)  # Chụp toàn bộ khung chứa khuôn mặt
            capture_flag = True  # Dừng vòng lặp sau khi chụp ảnh

    cv2.imshow('img', frame)

    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

    if capture_flag == True:
        image_path = '/Users/trantuan/Downloads/Face_Lock_IoT-main/Python/image/captured_face.jpg'
        image = Image.open(image_path)

        # Convert the image to a numpy array
        image_np = np.array(image)

        # Process the image using the existing function
        name = Server.process(image_np)
        print(name)
        time.sleep(2)
# Dòng này đảm bảo rằng cửa sổ hiển thị được đóng khi thoát khỏi vòng lặp
cv2.destroyAllWindows()
