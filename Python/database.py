import mysql.connector
from datetime import datetime

db_config = {
    'user': 'root',
    'password': '123456',
    'host': 'localhost',
    'database': 'face_recognition',
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

def addAttendanceTime(name):
    query = "INSERT INTO attendance (name, attendance_time) VALUES (%s, %s)"
    values = (name, datetime.now())
    cursor.execute(query, values)
    conn.commit()

def removeAttendanceTimeByKey(id):
    query = "DELETE FROM attendance WHERE id = %s"
    values = (id,)
    cursor.execute(query, values)
    conn.commit()