import cv2
from deepface import DeepFace

# Mở camera
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Không thể mở camera. Hãy kiểm tra kết nối.")
    exit()

print("Nhấn 'q' để thoát.")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Không thể đọc khung hình từ camera.")
        break

    try:
        # Phân tích cảm xúc từ khung hình
        analysis = DeepFace.analyze(frame, actions=['emotion'], enforce_detection=False)
        dominant_emotion = analysis[0]['dominant_emotion']

        # Hiển thị cảm xúc lên khung hình
        cv2.putText(frame, f"Cảm xúc: {dominant_emotion}", (10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2, cv2.LINE_AA)

    except Exception as e:
        print(f"Lỗi khi phân tích: {e}")

    # Hiển thị khung hình
    cv2.imshow("Nhận diện cảm xúc", frame)

    # Nhấn 'q' để thoát
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Giải phóng tài nguyên
cap.release()
cv2.destroyAllWindows()
