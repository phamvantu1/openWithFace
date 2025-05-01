from flask import Flask, jsonify
import speech_recognition as sr

from Python.ESP32 import send_command, send_command_string


# Hàm nhận diện giọng nói và thực hiện hành động
def recognize_speech():
    recognizer = sr.Recognizer()

    # Sử dụng microphone làm nguồn thu âm
    with sr.Microphone() as source:
        print("Hãy nói 'vào micro đi bạn'...")
        recognizer.adjust_for_ambient_noise(source)  # Cân chỉnh tiếng ồn xung quanh
        audio = recognizer.listen(source)

    try:
        # Nhận diện giọng nói từ Google Speech API
        command = recognizer.recognize_google(audio, language='vi-VN')
        print(f"Bạn đã nói: {command}")

        # Kiểm tra nếu người dùng nói "bắn"
        if "bắn" in command.lower():
            print(f" tôi đã nói bắn")
            send_command_string("open")
            return "Bắn"
        elif "sang trái" in command.lower():
            print(f" tôi đã nói sang trái ")
            send_command_string("left")
            return "sang trái"
        elif "sang phải" in command.lower():
            print(f" tôi đã nói sang phải")
            send_command_string("right")
            return "sang phải"
        elif "lên trên" in command.lower():
            print(f" tôi đã nói lên trên")
            send_command_string("up")
            return "lên trên"
        elif "xuống dưới" in command.lower():
            print(f" tôi đã nói xuống dưới")
            send_command_string("down")
            return "xuống dưới"
        else:
            return "Lệnh không rõ ràng"

    except sr.UnknownValueError:
        return "Không thể nhận diện giọng nói"
    except sr.RequestError as e:
        return f"Lỗi kết nối với Google Speech API; {0}".format(e)
