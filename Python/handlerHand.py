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
previous_positions = []

# Hàm kiểm tra xòe tay
def is_hand_open(landmarks):
    # Kiểm tra các ngón tay đang xòe
    fingers_open = []
    for finger_tip, finger_mcp in [
        (mp_hands.HandLandmark.THUMB_TIP, mp_hands.HandLandmark.THUMB_CMC),
        (mp_hands.HandLandmark.INDEX_FINGER_TIP, mp_hands.HandLandmark.INDEX_FINGER_MCP),
        (mp_hands.HandLandmark.MIDDLE_FINGER_TIP, mp_hands.HandLandmark.MIDDLE_FINGER_MCP),
        (mp_hands.HandLandmark.RING_FINGER_TIP, mp_hands.HandLandmark.RING_FINGER_MCP),
        (mp_hands.HandLandmark.PINKY_TIP, mp_hands.HandLandmark.PINKY_MCP),
    ]:
        # Ngón mở khi TIP cao hơn MCP theo trục Y (Y giảm khi lên trên)
        fingers_open.append(landmarks[finger_tip].y < landmarks[finger_mcp].y)
    # Nếu tất cả ngón đều mở thì xòe tay
    return all(fingers_open)

# Hàm kiểm tra vẫy tay
def detect_wave(landmarks):
    global last_wave_time, previous_positions

    # Vị trí của bàn tay (dựa vào lòng bàn tay)
    wrist = landmarks[mp_hands.HandLandmark.WRIST]

    # Lưu trữ vị trí của cổ tay (theo dõi chuyển động)
    current_position = (wrist.x, wrist.y)
    previous_positions.append(current_position)

    # Giới hạn số lượng vị trí lưu trữ
    if len(previous_positions) > 10:
        previous_positions.pop(0)

    # Kiểm tra sự thay đổi vị trí qua lại (vẫy tay)
    if len(previous_positions) > 1:
        # Tính sự thay đổi trong vị trí
        move_x = previous_positions[-1][0] - previous_positions[0][0]

        # Nếu có sự thay đổi đáng kể trong vị trí của cổ tay
        if abs(move_x) > 0.05:
            current_time = time.time()
            if current_time - last_wave_time > 1.5:  # Giới hạn thời gian giữa các lần vẫy tay
                last_wave_time = current_time
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

                # Kiểm tra nếu tay đang xòe
                if is_hand_open(hand_landmarks.landmark):
                    # Kiểm tra nếu có vẫy tay
                    if detect_wave(hand_landmarks.landmark):
                        print("Vẫy tay phát hiện: Mở cửa!")
                        # Ở đây bạn có thể thêm mã để mở cửa

        # Hiển thị khung hình
        cv2.imshow("Hand Gesture Detection", frame)

        # Nhấn phím 'q' để thoát
        if cv2.waitKey(5) & 0xFF == ord('q'):
            break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
