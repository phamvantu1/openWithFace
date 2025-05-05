from flask import Flask, jsonify
import speech_recognition as sr
from Python.ESP32 import send_command

import asyncio


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
        if "tấn công" in command.lower():
            print(f" tôi đã nói bắn")
            asyncio.run(send_command("Space"))
            return "Bắn"
        elif "sang trái" in command.lower():
            print(f" tôi đã nói sang trái ")
            asyncio.run(send_command("ArrowLeft"))
            return "sang trái"
        elif "sang phải" in command.lower():
            print(f" tôi đã nói sang phải")
            asyncio.run(send_command("ArrowRight"))
            return "sang phải"
        elif "lên trên" in command.lower():
            print(f" tôi đã nói lên trên")
            asyncio.run(send_command("ArrowUp"))
            return "lên trên"
        elif "xuống dưới" in command.lower():
            print(f" tôi đã nói xuống dưới")
            asyncio.run(send_command("ArrowDown"))
            return "xuống dưới"
        else:
            return "Lệnh không rõ ràng"

    except sr.UnknownValueError:
        return "Không thể nhận diện giọng nói"
    except sr.RequestError as e:
        return f"Lỗi kết nối với Google Speech API; {0}".format(e)
