from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import pyotp
import speech_recognition as sr
import mysql.connector
from mysql.connector import Error

from Python.ESP32 import send_command
from Python.Send_Email import send_email_with_image
from Python.database import getAttendanceTime, addAttendanceTime, addAttendanceTimeV2
from Python.voiceController import recognize_speech

app = Flask(__name__)
CORS(app)  # Cho phép CORS cho mọi nguồn
UPLOAD_FOLDER = './ImageAttendance'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Bí mật dùng để sinh OTP (bạn có thể tạo ngẫu nhiên)
SECRET_KEY = pyotp.random_base32()

# MySQL database configuration
db_config = {
    'user': 'root',
    'password': '123456',
    'host': 'localhost',
    'database': 'smartdoor',
}

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

@app.route('/voice-command', methods=['GET'])
def voice_command():
    # Nhận diện giọng nói và trả về kết quả
    result = recognize_speech()
    return jsonify({'command': result})

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