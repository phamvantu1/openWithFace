import mysql.connector
from datetime import datetime

db_config = {
    'user': 'root',
    'password': '',
    'host': 'localhost',
    'database': 'smartdoor',
}

conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

def addAttendanceTime(name):
    query = "INSERT INTO action (card_number, action_type, status, timestamp) VALUES (%s, %s, %s, %s)"
    values = (name,"faceID","success", datetime.now())
    cursor.execute(query, values)
    conn.commit()


def addAttendanceTimeV2(name):
    query = "INSERT INTO action (card_number, action_type, status, timestamp) VALUES (%s, %s, %s, %s)"
    values = (name,"web","success", datetime.now())
    cursor.execute(query, values)
    conn.commit()

def getAttendanceTime():
    cursor.execute("SELECT * FROM action")
    actions = cursor.fetchall()
    return actions

def removeAttendanceTimeByKey(id):
    query = "DELETE FROM action WHERE id = %s"
    values = (id,)
    cursor.execute(query, values)
    conn.commit()
