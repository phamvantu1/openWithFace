import cv2
import numpy as np
import socket
import time
import requests
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
SEND_INTERVAL = 1  # Gửi lệnh mỗi 200ms
SAFE_ZONE_WIDTH = 160  # Chiều rộng vùng an toàn
SAFE_ZONE_HEIGHT = 120  # Chiều cao vùng an toàn
MAX_HISTORY = 5  # Số giá trị cho bộ lọc trung bình

esp32_ip = "192.168.218.173"
esp32_port = 5000
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

class MJPEGStream:
    def __init__(self, url):
        self.stream = cv2.VideoCapture(url)
        self.frame = None
        self.running = True
        import threading
        threading.Thread(target=self.update, daemon=True).start()

    def update(self):
        while self.running:
            ret, frame = self.stream.read()
            if ret:
                self.frame = frame

    def read(self):
        return self.frame

    def stop(self):
        self.running = False
        self.stream.release()

cap = MJPEGStream("http://192.168.218.72:81/stream")

tracker = None
tracking = False
current_object = None
cx_history = []
cy_history = []

# cap = cv2.VideoCapture(0)
# if not cap.isOpened():
#     print("❌ Không mở được camera")
#     exit()

while True:
    frame = cap.read()
    if frame is None:
        print("❌ Không đọc được frame từ camera")
        continue

    frame = cv2.resize(frame, (640, 480))
    frame = cv2.flip(frame, 0)
    key = cv2.waitKey(1) & 0xFF
    now = time.time()

    if key == 27:
        break

    if tracking and tracker is not None:
        success, box = tracker.update(frame)
        if success:
            x, y, w, h = [int(v) for v in box]
            cx, cy = x + w // 2, y + h // 2

            # Lọc tọa độ bằng trung bình động
            cx_history.append(cx)
            cy_history.append(cy)
            if len(cx_history) > MAX_HISTORY:
                cx_history.pop(0)
                cy_history.pop(0)

            cx_smooth = int(sum(cx_history) / len(cx_history))
            cy_smooth = int(sum(cy_history) / len(cy_history))

            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.circle(frame, (cx_smooth, cy_smooth), 5, (0, 0, 255), -1)

            # Vẽ vùng an toàn (320x240) để debug
            safe_zone_x1 = 320 - SAFE_ZONE_WIDTH // 2  # 160
            safe_zone_x2 = 320 + SAFE_ZONE_WIDTH // 2  # 480
            safe_zone_y1 = 240 - SAFE_ZONE_HEIGHT // 2  # 120
            safe_zone_y2 = 240 + SAFE_ZONE_HEIGHT // 2  # 360
            cv2.rectangle(frame, (safe_zone_x1, safe_zone_y1), (safe_zone_x2, safe_zone_y2), (255, 255, 0), 1)

            # # Tính offset để đưa tâm về (320, 240)
            # offset_x = cx_smooth - 320
            # offset_y = cy_smooth - 240

            # Tính offset so với vùng an toàn
            offset_x = 0
            offset_y = 0

            if cx_smooth < safe_zone_x1:
                offset_x = cx_smooth - safe_zone_x1  # lệch trái
            elif cx_smooth > safe_zone_x2:
                offset_x = cx_smooth - safe_zone_x2  # lệch phải

            if cy_smooth < safe_zone_y1:
                offset_y = cy_smooth - safe_zone_y1  # lệch lên
            elif cy_smooth > safe_zone_y2:
                offset_y = cy_smooth - safe_zone_y2  # lệch xuống

            # Kiểm tra xem tâm có trong vùng an toàn không
            in_safe_zone = (safe_zone_x1 <= cx_smooth <= safe_zone_x2) and (safe_zone_y1 <= cy_smooth <= safe_zone_y2)

            # print(f"🟢 Tâm vật: cx={cx_smooth}, cy={cy_smooth}, offset_x={offset_x}, offset_y={offset_y}, Trong vùng an toàn: {in_safe_zone}")

            if now - last_sent_time >= SEND_INTERVAL and not in_safe_zone:
                # print(f"📤 Gửi offset X: {offset_x}, Y: {offset_y}")
                send_command(offset_x, offset_y)  # Gửi offset ngược dấu cho Y
                last_sent_time = now
            elif in_safe_zone:
                b = 1;
                # print("🔇 Trong vùng an toàn, không gửi lệnh")
        else:
            print("🔴 Mất dấu vật đang theo dõi.")
            tracking = False
            current_object = None
            cx_history.clear()
            cy_history.clear()
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

                if confidence > 0.95:  # Tăng ngưỡng để nhận diện chính xác hơn
                    detected_label = labels[label_idx]
                    print(f"🟢 Nhận diện: {detected_label} ({confidence:.2f})")

                    if detected_label == "2 C":
                        tracking = False
                        tracker = None
                        current_object = None
                        print("🛑 Dừng theo dõi do phát hiện vật C")

                    elif detected_label in ["0 A", "1 B"]:
                        x = frame.shape[1]//2 - 75  # 320 - 75 = 245
                        y = frame.shape[0]//2 - 75  # 240 - 75 = 165
                        box = (x, y, 160, 120)  # Hộp 150x150, tâm tại (320, 240)

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