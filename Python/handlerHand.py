import cv2
import mediapipe as mp
import time

# Khởi tạo MediaPipe Hands
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

# Khởi tạo Camera
cap = cv2.VideoCapture(0)

# Biến theo dõi thời gian để phát hiện vẫy tay
last_wave_time = 0
wave_detected = False
previous_positions = []


# Hàm kiểm tra vẫy tay
def detect_wave(landmarks):
    global last_wave_time, wave_detected, previous_positions

    # Vị trí của ngón cái và ngón trỏ
    thumb_tip = landmarks[mp_hands.HandLandmark.THUMB_TIP]
    index_tip = landmarks[mp_hands.HandLandmark.INDEX_FINGER_TIP]

    # Lưu trữ vị trí của các ngón tay trong danh sách (theo dõi chuyển động)
    current_position = (thumb_tip.x, thumb_tip.y, index_tip.x, index_tip.y)

    # Thêm vị trí mới vào danh sách
    previous_positions.append(current_position)

    # Giới hạn số lượng vị trí lưu trữ
    if len(previous_positions) > 10:
        previous_positions.pop(0)

    # Kiểm tra sự thay đổi vị trí qua lại (vẫy tay)
    if len(previous_positions) > 1:
        # Tính sự thay đổi trong vị trí
        thumb_move = previous_positions[-1][0] - previous_positions[0][0]
        index_move = previous_positions[-1][2] - previous_positions[0][2]

        # Nếu có sự thay đổi đáng kể trong vị trí của ngón cái và ngón trỏ (vẫy tay)
        if abs(thumb_move) > 0.05 or abs(index_move) > 0.05:
            current_time = time.time()
            if current_time - last_wave_time > 1.5:  # Giới hạn thời gian giữa các lần vẫy tay
                last_wave_time = current_time
                wave_detected = True
                return True
    return False


# Khởi tạo bộ xử lý bàn tay
with mp_hands.Hands(max_num_hands=1, min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Không thể truy cập camera.")
            break

        # Lật ảnh để giống như gương
        frame = cv2.flip(frame, 1)

        # Chuyển đổi màu sắc từ BGR sang RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = hands.process(rgb_frame)

        # Nếu phát hiện bàn tay
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Vẽ các điểm trên bàn tay
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Phát hiện vẫy tay
                if detect_wave(hand_landmarks.landmark):
                    print("Vẫy tay phát hiện: Mở cửa!")
                    wave_detected = False
                    # Ở đây bạn có thể thêm mã để mở cửa, ví dụ: gửi tín hiệu đến Raspberry Pi hoặc Arduino

        # Hiển thị khung hình
        cv2.imshow("Hand Gesture Detection", frame)

        # Nhấn phím 'q' để thoát
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
