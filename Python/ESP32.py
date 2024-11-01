import socket
import time

esp32_ip = "192.168.0.104"
esp32_port = 80

def send_command(command):
    print(command)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((esp32_ip, esp32_port))
            s.sendall(command.encode())
    except ConnectionRefusedError:
        print("Connection refused. Ensure ESP32 server is running.")
    time.sleep(1)