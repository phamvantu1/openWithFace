import cv2

import tensorflow as tf

print(cv2.__version__)


print(tf.__version__)


# img_path = "D:\IOT\openWithFace\openWithFace\Python\ImageAttendance\smile.jpg"


from fer import FER
from PIL import Image
import numpy as np

# Đường dẫn đến hình ảnh
img_path = "D:\IOT\openWithFace\openWithFace\Python\ImageAttendance\smile.jpg"
# Mở ảnh bằng Pillow
image = Image.open(img_path)

# Chuyển ảnh thành mảng numpy
image_array = np.array(image)

# Khởi tạo công cụ phát hiện cảm xúc
emotion_detector = FER(mtcnn=True)  # Sử dụng MTCNN để phát hiện khuôn mặt tốt hơn

# Phát hiện cảm xúc
emotion, score = emotion_detector.top_emotion(image_array)

# Kết quả
if emotion:
    print(f"Detected emotion: {emotion} with score: {score}")
else:
    print("No face detected or emotion could not be identified.")
