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

url = 'http://192.168.83.72/cam-lo.jpg'

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

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Variables for hand gesture detection
last_wave_time = 0
previous_positions = []

def is_hand_open(landmarks):
    fingers_open = []
    for finger_tip, finger_mcp in [
        (mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.THUMB_CMC),
        (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_MCP),
        (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_MCP),
        (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_MCP),
        (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_MCP),
    ]:
        fingers_open.append(landmarks[finger_tip].y < landmarks[finger_mcp].y)
    return all(fingers_open)

def detect_wave(landmarks):
    global last_wave_time, previous_positions
    wrist = landmarks[mp_hands.HandLandmark.WRIST]
    current_position = (wrist.x, wrist.y)
    previous_positions.append(current_position)
    if len(previous_positions) > 10:
        previous_positions.pop(0)
    if len(previous_positions) > 1:
        move_x = previous_positions[-1][0] - previous_positions[0][0]
        if abs(move_x) > 0.05:
            current_time = time.time()
            if current_time - last_wave_time > 1.5:
                last_wave_time = current_time
                return True
    return False

with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
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
                if emotion == 'sad':
                    print("buồn")
                    send_esp8266("open")
                if emotion == 'happy':
                    print("vui")
                if emotion == 'angry':
                    print("tức giận")
                    send_esp8266("open")
                print(f"Detected emotion: {emotion} with score: {score}")

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                if is_hand_open(hand_landmarks.landmark):
                    if detect_wave(hand_landmarks.landmark):
                        print("Wave detected: Open door!")
                        # Add code to open the door
                        send_command("open")

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