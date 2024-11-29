from flask import Flask, jsonify, request
import pyotp

app = Flask(__name__)

# Bí mật dùng để sinh OTP (bạn có thể tạo ngẫu nhiên)
SECRET_KEY = pyotp.random_base32()


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
            return jsonify({'error': 'Vui lòng cung cấp mã OTP'}), 400

        # Tạo đối tượng OTP
        totp = pyotp.TOTP(SECRET_KEY, interval=30)

        # Kiểm tra mã OTP
        if totp.verify(otp):
            return jsonify({'message': 'OTP hợp lệ'}), 200
        else:
            return jsonify({'message': 'OTP không hợp lệ hoặc đã hết hạn'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)


