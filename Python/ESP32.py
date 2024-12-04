import socket
import time

# esp32_ip = "192.168.226.153"
esp32_ip = "192.168.83.153"
esp32_port = 80

esp8266_ip = "192.168.83.130"
esp8266_port = 80

def send_command(command):
    print(command)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((esp32_ip, esp32_port))
            s.sendall(command.encode())
    except ConnectionRefusedError:
        print("Connection refused. Ensure ESP32 server is running.")
    time.sleep(1)

def send_esp8266(command):
    print(f"Sending command: {command}")
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((esp8266_ip, esp8266_port))
            s.sendall(command.encode())  # Send command
    except ConnectionResetError:
        print("Connection was reset by the server (ESP8266). Ensure server handles the request properly.")
    except Exception as e:
        print(f"An error occurred: {e}")
    time.sleep(1)
