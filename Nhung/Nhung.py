import cv2
import numpy as np
import socket
import time
import tensorflow as tf
from tensorflow.keras.models import load_model
from tensorflow.keras.layers import DepthwiseConv2D

print(f"TensorFlow version: {tf.__version__}")
print(f"NumPy version: {np.__version__}")
try:
    import google.protobuf
    print(f"Protobuf version: {google.protobuf.__version__}")
except ImportError:
    print("Protobuf không được cài đặt")

# Custom DepthwiseConv2D
class CustomDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, *args, **kwargs):
        kwargs.pop('groups', None)
        super().__init__(*args, **kwargs)

# Load model
try:
    model = load_model("keras_model_1.h5", custom_objects={'DepthwiseConv2D': CustomDepthwiseConv2D})
    print("✅ Đã tải mô hình thành công")
except Exception as e:
    print(f"❌ Lỗi tải mô hình: {e}")
    exit()

# Load labels
try:
    labels = open("labels_1.txt", "r").read().splitlines()
    print(f"✅ Đã tải {len(labels)} nhãn")
except Exception as e:
    print(f"❌ Lỗi tải labels.txt: {e}")
    exit()

IMG_SIZE = (224, 224)

esp32_ip = "192.168.237.173"
esp32_port = 5000
SEND_INTERVAL = 1
last_sent_time = 0
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((esp32_ip, esp32_port))
    print("✅ Đã kết nối ESP32")
except ConnectionRefusedError:
    print("❌ Không kết nối được ESP32")
    exit()

def send_command(offset_x, offset_y):
    try:
        message = f"{offset_x},{offset_y}\n"
        s.sendall(message.encode())
        print(f"📤 Gửi offset X: {offset_x}, Y: {offset_y}")
    except Exception as e:
        print(f"❌ Lỗi gửi dữ liệu: {e}")

cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("❌ Không mở được camera")
    exit()

tracker = None
tracking = False
current_object = None

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Không đọc được frame từ camera")
        continue

    frame = cv2.flip(frame, 1)
    key = cv2.waitKey(1) & 0xFF
    now = time.time()

    if key == 27:
        break

    if tracking and tracker is not None:
        success, box = tracker.update(frame)
        if success:
            x, y, w, h = [int(v) for v in box]
            cx, cy = x + w // 2, y + h // 2
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)

            offset_x = cx - frame.shape[1] // 2
            offset_y = cy - frame.shape[0] // 2

            if now - last_sent_time >= SEND_INTERVAL:
                send_command(offset_x, offset_y)
                last_sent_time = now
        else:
            print("🔴 Mất dấu vật đang theo dõi.")
            tracking = False
            current_object = None
    else:
        center_crop = frame[
            frame.shape[0]//2 - 112:frame.shape[0]//2 + 112,
            frame.shape[1]//2 - 112:frame.shape[1]//2 + 112
        ]

        if center_crop.shape[:2] == (224, 224):
            input_image = cv2.resize(center_crop, IMG_SIZE)
            input_image = cv2.cvtColor(input_image, cv2.COLOR_BGR2RGB)
            input_image = np.expand_dims(input_image, axis=0)
            input_image = (input_image.astype(np.float32) / 127.5) - 1

            try:
                predictions = model.predict(input_image, verbose=0)[0]
                label_idx = np.argmax(predictions)
                confidence = predictions[label_idx]

                if confidence > 0.9:
                    detected_label = labels[label_idx]
                    print(f"🟢 Nhận diện: {detected_label} ({confidence:.2f})")

                    if detected_label == "2 C":
                        tracking = False
                        tracker = None
                        current_object = None
                        print("🛑 Dừng theo dõi do phát hiện vật C")

                    elif detected_label in ["0 A", "1 B"]:
                        x = frame.shape[1]//2 - 50
                        y = frame.shape[0]//2 - 50
                        box = (x, y, 100, 100)

                        tracker = cv2.TrackerCSRT_create()
                        tracker.init(frame, box)
                        tracking = True
                        current_object = detected_label
                        print(f"🚀 Bắt đầu theo dõi {detected_label}")

            except Exception as e:
                print(f"❌ Lỗi dự đoán mô hình: {e}")

    cv2.imshow("TeachableMachine Tracking", frame)

cap.release()
cv2.destroyAllWindows()
if s is not None:
    s.close()
