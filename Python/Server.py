import time
import sys
import cv2
import numpy as np
import face_recognition
import os
from datetime import datetime
import mysql.connector  # Add this import
import requests
from ESP32 import send_command
# MySQL database configuration
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'smartdoor',
}
BASE_URL = "http://192.168.102.3:5000"
image_folder = os.path.join(os.getcwd(), 'public', 'images')

# Initialize MySQL connection and cursor
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

path = './ImageAttendance'
images = []
classNames = []
stime = 0
unlock = False
myList = os.listdir(path)
print(myList)
for cl in myList:
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

#  nhan dien khuon mat  va ma hoa chung thanh mot dãy số duy nhất
def findEncodings(images):
    encodeList = []
    for img in images:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList


encodeListKnown = findEncodings(images)
print('Encoding Complete')

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

if not cap.isOpened():
    sys.exit('Video source not found...')


def process(img):
    name = "User does not exist"
    global stime
    global unlock
    global isHost

    imgS = cv2.resize(img, (0, 0), None, fx=0.25, fy=0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    facesCurFrame = face_recognition.face_locations(imgS)
    encodesCurFrame = face_recognition.face_encodings(imgS, facesCurFrame)

    etime = datetime.now().strftime('%S')

    for encodeFace, faceLoc in zip(encodesCurFrame, facesCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        print(faceDis)
        matchIndex = np.argmin(faceDis)
        #  khoang cach la khoang cách euclid giữa các khuôn mặt , tại các anh được biểu diễn dưới dạng vector
        if faceDis[matchIndex] < 0.50:
            name = classNames[matchIndex].upper()
            add_attendance_time(name)
            unlock = True
            if name == "HOST":
                isHost = True
                unlock = False
            else:
                isHost = False
        else:
            name = 'Unknown'

        y1, x2, y2, x1 = faceLoc
        y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)
        cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0, 255, 0), cv2.FILLED)
        cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)

    if unlock:
        time.sleep(1)
        send_command("open")
        print("open1")
        unlock = False
    # if isHost :
    #     print("day la host")
    #     send_command("host")
    #     isHost = False

    cv2.imshow('Webcam', img)
    cv2.waitKey(1)

    return name

def add_attendance_time(name):
    query = "INSERT INTO action (card_number, action_type, status, timestamp, image) VALUES (%s, %s, %s, %s, %s)"
    image_url =  BASE_URL + "/get-image"
    path_i = downloadImageAndSave(image_url)
    values = (name, "faceID", "success", datetime.now(), path_i)
    cursor.execute(query, values)
    conn.commit()
    
    
def downloadImageAndSave(image_url):
    # Đặt tên file ảnh dựa trên timestamp
    image_filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}.jpg"
    image_path = os.path.join(image_folder, image_filename)

    try:
        # Tải ảnh từ URL
        response = requests.get(image_url, stream=True)
        if response.status_code == 200:
            with open(image_path, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            print(f"Image saved at {image_path}")
            image_url = f"{BASE_URL}/getimages/{image_filename}"
            return image_url
            # return image_path


        else:
            print(f"Failed to download image, status code: {response.status_code}")

    except Exception as e:
        print(f"Error downloading image: {e}")
    

cv2.destroyAllWindows()


