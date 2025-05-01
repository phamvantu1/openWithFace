import socket
import time

# esp32_ip = "192.168.226.153"
# esp32_ip = "192.168.83.153"
# esp32_port = 80
#
# esp8266_ip = "192.168.83.130"
# esp8266_port = 80


esp32_ip = "192.168.218.173"
esp32_port = 5000
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
last_send_time = 0
min_send_interval = 0.1  # Giới hạn gửi lệnh mỗi 100ms



# Kết nối với ESP32
def connect_to_esp32():
    global s
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((esp32_ip, esp32_port))
        s.setblocking(False)
        print("✅ Đã kết nối ESP32")
        return True
    except ConnectionRefusedError:
        print("❌ Không kết nối được ESP32")
        return False

# Gửi lệnh 2 tham số
def send_command(offset_x, offset_y):
    global last_send_time
    current_time = time.time()
    if current_time - last_send_time < min_send_interval:
        return False  # Bỏ qua nếu gửi quá nhanh
    try:
        message = f"{offset_x},{offset_y}\n"
        s.sendall(message.encode())
        print(f"📤 Gửi lệnh di chuyển: X = {offset_x}, Y = {offset_y}")
        last_send_time = current_time
        return True
    except Exception as e:
        print(f"❌ Lỗi gửi dữ liệu: {e}")
        connect_to_esp32()  # Thử kết nối lại
        return False


# Gửi lệnh 1 chuỗi
def send_command_string(command_str):
    global last_send_time
    current_time = time.time()
    if current_time - last_send_time < min_send_interval:
        return False  # Gửi quá nhanh
    try:
        message = f"{command_str}\n"
        s.sendall(message.encode())
        print(f"📤 Gửi lệnh chuỗi: {command_str}")
        last_send_time = current_time
        return True
    except Exception as e:
        print(f"❌ Lỗi gửi chuỗi: {e}")
        connect_to_esp32()
        return False




#  hàm cũ sent 1 tham số
# def send_command(command):
#     print(command)
#     try:
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
#             s.connect((esp32_ip, esp32_port))
#             s.sendall(command.encode())
#     except ConnectionRefusedError:
#         print("Connection refused. Ensure ESP32 server is running.")
#     time.sleep(1)
#

