from flask import Flask, request, jsonify, send_from_directory, render_template
from flask_cors import CORS
import time
import os
import pyotp
import speech_recognition as sr
import mysql.connector
from mysql.connector import Error
import socket

from Python.ESP32 import send_command, send_command_string
from Python.Send_Email import send_email_with_image
from Python.database import getAttendanceTime, addAttendanceTime, addAttendanceTimeV2, check_user_login, \
    get_shoot_history, save_shoot_history, get_discovery_history, save_discovery_history, get_first_bullet
from Python.voiceController import recognize_speech
from flask import session
import secrets


app = Flask(__name__)
CORS(app)  # Cho phép CORS cho mọi nguồn
UPLOAD_FOLDER = './ImageAttendance'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Bí mật dùng để sinh OTP (bạn có thể tạo ngẫu nhiên)
SECRET_KEY = pyotp.random_base32()
#  khoá bí mật cho session
app.secret_key = secrets.token_hex(16)  # Tạo khóa ngẫu nhiên 16 byte (32 ký tự hex)



# MySQL database configuration
db_config = {
    'user': 'root',
    'password': '123456',
    'host': 'localhost',
    'database': 'nhungiot',
}

 # api để bắn
@app.route('/open', methods=['POST'])
def send_custom_command():
    try:
        data = request.get_json()
        command = data.get('command')

        if not command:
            return jsonify({"status": "error", "message": "Thiếu trường 'command'"}), 400

        if send_command_string(command):
            return jsonify({"status": "success", "message": f"Lệnh '{command}' đã được gửi"}), 200
        else:
            return jsonify({"status": "error", "message": "Gửi lệnh thất bại hoặc gửi quá nhanh"}), 429
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


# API điều khiển Servo
@app.route('/control', methods=['POST'])
def control_servo():
    try:
        data = request.get_json()
        offset_x = data.get('offset_x', 0)
        offset_y = data.get('offset_y', 0)

        if offset_x == 0 and offset_y == 0:
            return jsonify({"status": "error", "message": "Không có lệnh di chuyển được gửi"}), 400

        if send_command(offset_x, offset_y):
            return jsonify({"status": "success", "message": "Lệnh di chuyển đã được gửi thành công"}), 200
        else:
            return jsonify({"status": "error", "message": "Gửi lệnh thất bại hoặc gửi quá nhanh"}), 429
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

#  API nhận diện giọng nói
@app.route('/voice-command', methods=['GET'])
def voice_command():
    # Nhận diện giọng nói và trả về kết quả
    result = recognize_speech()
    return jsonify({'command': result})



#  api login
@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({"status": "error", "message": "Thiếu username hoặc password"}), 400

        user = check_user_login(username, password)

        if user:
            return jsonify({
                "status": "success",
                "message": "Đăng nhập thành công",
                "user": {"id": user["id"], "username": user["username"]}
            })
        else:
            return jsonify({"status": "error", "message": "Sai username hoặc password"}), 401

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


#  api đăng xuất
@app.route('/logout', methods=['POST'])
def logout():
    try:
        session.pop('user_id', None)  # Xóa thông tin người dùng khỏi session
        return jsonify({
            "status": "success",
            "message": "Đăng xuất thành công"
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


#  api lịch sử bắn
@app.route('/shoot_history', methods=['GET'])
def shoot_history():
    try:
        # Lấy tham số page và size từ query string, mặc định page=1, size=10
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))

        # Lấy dữ liệu phân trang
        history = get_shoot_history(page, size)

        if history:
            return jsonify({
                "status": "success",
                "message": "Lịch sử bắn được lấy thành công",
                "page": page,
                "size": size,
                "data": history
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Không tìm thấy lịch sử bắn"
            }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



#  api lưu lịch sử bắn
@app.route('/save-shoot-history', methods=['POST'])
def create_shoot_history():
    try:
        data = request.get_json()
        username = data.get('username')
        status = data.get('status', 'unknown')  # Nếu không truyền status, mặc định là 'unknown'

        if not username:
            return jsonify({"status": "error", "message": "Thiếu trường 'username'"}), 400

        success = save_shoot_history(username, status)

        if success:
            return jsonify({"status": "success", "message": "Lưu lịch sử bắn thành công"}), 200
        else:
            return jsonify({"status": "error", "message": "Lưu lịch sử bắn thất bại"}), 500
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

#  api để nạp đạn
@app.route('/reload', methods=['POST'])
def reload():
    try:
        command = 'reload'
        print("chuoi gui di la :   " + command)

        if not command:
            return jsonify({"status": "error", "message": "Thiếu trường 'command'"}), 400

        if send_command_string(command):
            return jsonify({"status": "success", "message": f"Lệnh '{command}' đã được gửi"}), 200
        else:
            return jsonify({"status": "error", "message": "Gửi lệnh thất bại hoặc gửi quá nhanh"}), 429
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


#  api lịch sử phát hiện
@app.route('/discovery-history', methods=['GET'])
def fetch_discovery_history():
    try:
        # Lấy tham số page và limit từ query string, mặc định page=1, limit=10
        page = int(request.args.get('page', 1))
        size = int(request.args.get('size', 10))

        data = get_discovery_history(page, size)
        if data is not None and len(data) > 0:
            return jsonify({
                "status": "success",
                "page": page,
                "size": size,
                "data": data
            }), 200
        else:
            return jsonify({"status": "error", "message": "Không tìm thấy lịch sử discovery"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


#  api lưu lại lịch sử phat hiện
@app.route('/save-discovery-history', methods=['POST'])
def add_discovery_history():
    try:
        data = request.get_json()
        method = data.get('method')
        distance = data.get('distance')

        if not method or distance is None:
            return jsonify({
                "status": "error",
                "message": "Missing 'method' or 'distance' in request"
            }), 400

        success = save_discovery_history(method, distance)
        if success:
            return jsonify({
                "status": "success",
                "message": "Lưu lịch sử phát hiện thành công"
            }), 201
        else:
            return jsonify({
                "status": "error",
                "message": "Không thể lưu lịch sử phát hiện"
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


#  api lấy ra số đạn còn lại
@app.route('/bullet/first', methods=['GET'])
def fetch_first_bullet():
    try:
        data = get_first_bullet()
        if data:
            return jsonify({
                "status": "success",
                "data": data
            }), 200
        else:
            return jsonify({
                "status": "error",
                "message": "Không tìm thấy viên đạn nào"
            }), 404
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500



























@app.route('/')
def index():
    return render_template('main.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return jsonify({'success': 'File uploaded successfully'}), 200

@app.route('/delete', methods=['POST'])
def delete_file():
    data = request.get_json()
    filename = data.get('filename')
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        return jsonify({'success': 'File deleted successfully'}), 200
    else:
        return jsonify({'error': 'File not found'}), 404

@app.route('/list', methods=['GET'])
def list_files():
    files = os.listdir(app.config['UPLOAD_FOLDER'])
    return jsonify({'files': files}), 200

@app.route('/images/<filename>', methods=['GET'])
def get_image(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/open-door', methods=['POST'])
def open_door():
    send_command("open")
    addAttendanceTimeV2("openByAPP")
    return jsonify({'success': 'Door opened successfully'}), 200

@app.route('/history', methods=['GET'])
def get_actions():
    actions = getAttendanceTime()
    return jsonify({'actions': actions}), 200



# Hàm API để sinh OTP
@app.route('/generate-otp', methods=['GET'])
def generate_otp():
    try:
        # Tạo đối tượng OTP với thời gian hết hạn 30 giây
        totp = pyotp.TOTP(SECRET_KEY, interval=30)

        # Sinh OTP
        otp = totp.now()

        # Trả về OTP và thời gian hết hạn
        return jsonify({
            'otp': otp,
            'expires_in': 30  # OTP hết hạn sau 30 giây
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Hàm API để xác minh OTP
@app.route('/verify-otp', methods=['POST'])
def verify_otp():
    try:
        data = request.json
        otp = data.get('otp')  # OTP từ client gửi lên

        if not otp:
            return jsonify({'doorStatus': 0, 'message': 'OTP is missing'}), 400

        # Tạo đối tượng OTP
        totp = pyotp.TOTP(SECRET_KEY, interval=30)

        # Kiểm tra mã OTP
        if totp.verify(otp):
            return jsonify({'doorStatus': 1, 'message': 'OTP verified successfully'}), 200
        else:
            return jsonify({'doorStatus': 0, 'message': 'Invalid OTP'}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500



# check pass cong 5000
@app.route('/check_pass', methods=['POST'])
def checkpass():
    try:
        # Kết nối đến cơ sở dữ liệu
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Nhận từ khóa từ body của request
        data = request.json
        keyword = data.get('keyword')

        # Truy vấn kiểm tra mật khẩu
        query = "SELECT * FROM user_iot WHERE passdoor = %s"
        cursor.execute(query, (keyword,))
        results = cursor.fetchall()

        if results:
            # Nếu tìm thấy, lưu thông tin vào bảng action
            action_query = """
                INSERT INTO action (card_number, action_type, status)
                VALUES (%s, %s, %s)
            """
            action_values = ("Pass", "keypad", "SUCCESS")

            cursor.execute(action_query, action_values)
            connection.commit()

            print('Dữ liệu đã được lưu vào bảng action.')
            return jsonify({"doorStatus": 1, "message": "Access success."})
        else:
            # Không tìm thấy mật khẩu
            return jsonify({"doorStatus": 0, "message": "Access denied."})

    except Error as e:
        print("Lỗi truy vấn hoặc kết nối:", e)
        return jsonify({"message": "Internal Server Error"}), 500

    finally:
        # Đóng kết nối
        if connection.is_connected():
            cursor.close()
            connection.close()

#  gui email port 5000
@app.route('/send-email', methods=['POST'])
def send_email():
    to_email = "tutupham5@gmail.com"
    subject = "Đây là email cảnh báo có người đột nhập gửi đến phamtu"
    body = "Xin chào bạn, nhà bạn đang có người cố gắng xâm nhập trái phép. Đây là hình ảnh của họ."
    image_path = "D:/IOT/openWithFace/openWithFace/Python/image/captured_face.jpg"

    if not all([to_email, subject, body, image_path]):
        return jsonify({"error": "Thiếu dữ liệu. Vui lòng gửi đủ thông tin."}), 400

    result = send_email_with_image(to_email, subject, body, image_path)
    return jsonify({"message": result})

if __name__ == '__main__':
    # app.run(port=5000)
    app.run(host='0.0.0.0', port=5000)