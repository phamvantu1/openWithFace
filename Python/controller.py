from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os

from Python.ESP32 import send_command
from Python.database import getAttendanceTime, addAttendanceTime, addAttendanceTimeV2

app = Flask(__name__)
CORS(app)  # Cho phép CORS cho mọi nguồn
UPLOAD_FOLDER = './ImageAttendance'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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

if __name__ == '__main__':
    app.run(port=5000)