import mysql.connector
from datetime import datetime
import os
import requests
db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'smartdoor',
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()
# Thư mục lưu ảnh
image_folder = os.path.join(os.getcwd(), 'public', 'images')
if not os.path.exists(image_folder):
    os.makedirs(image_folder)

def addAttendanceTime(name):

    query = "INSERT INTO action (card_number, action_type, status, timestamp, image) VALUES (%s, %s, %s, %s, %s)"
    image_url = "http://127.0.0.1:5000/get-image"
    path_i = downloadImageAndSave(image_url)
    values = (name,"faceID","success", datetime.now(), path_i)
    cursor.execute(query, values)
    conn.commit()


def addAttendanceTimeV2(name):
    query = "INSERT INTO action (card_number, action_type, status, timestamp, image) VALUES (%s, %s, %s, %s, %s)"
    image_url = "http://127.0.0.1:5000/get-image"
    path_i = downloadImageAndSave(image_url)
    values = (name,"web","success", datetime.now(), path_i)
    cursor.execute(query, values)
    conn.commit()

def getAttendanceTime():
    cursor.execute("SELECT * FROM action")
    actions = cursor.fetchall()
    return actions

def removeAttendanceTimeByKey(id):
    query = "DELETE FROM action WHERE id = %s"
    values = (id,)
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
            image_url = f"http://127.0.0.1:5000/getimages/{image_filename}"
            return image_url
            # return image_path


        else:
            print(f"Failed to download image, status code: {response.status_code}")

    except Exception as e:
        print(f"Error downloading image: {e}")
