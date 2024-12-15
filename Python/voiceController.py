from flask import Flask, jsonify
import speech_recognition as sr

from ESP32 import send_command


# Hàm nhận diện giọng nói và thực hiện hành động
def recognize_speech():
    recognizer = sr.Recognizer()

    # Sử dụng microphone làm nguồn thu âm
    with sr.Microphone() as source:
        print("Hãy nói 'Mở cửa'...")
        recognizer.adjust_for_ambient_noise(source)  # Cân chỉnh tiếng ồn xung quanh
        audio = recognizer.listen(source)

    try:
        # Nhận diện giọng nói từ Google Speech API
        command = recognizer.recognize_google(audio, language='vi-VN')
        print(f"Bạn đã nói: {command}")

        # Kiểm tra nếu người dùng nói "mở cửa"
        if "mở cửa" in command.lower():
            print(f" toi da mo cua roi ")
            send_command("open")
            return "Mở cửa"
        else:
            return "Lệnh không rõ ràng"

    except sr.UnknownValueError:
        return "Không thể nhận diện giọng nói"
    except sr.RequestError as e:
        return f"Lỗi kết nối với Google Speech API; {0}".format(e)
