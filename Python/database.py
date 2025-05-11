import mysql.connector
from datetime import datetime

from mysql.connector import Error

db_config = {
    'user': 'root',
    'password': '123456',
    'host': 'localhost',
    'database': 'nhungiot',
}

conn = mysql.connector.connect(**db_config)
# cursor = conn.cursor()
cursor = conn.cursor(dictionary=True)

# Đăng nhập
def check_user_login(username, password):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    except Error as e:
        print(f"Error during login: {str(e)}")
        return None

# Lấy lịch sử bắn
def get_shoot_history(page, size):
    try:
        offset = (page - 1) * size
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM history_shoot ORDER BY time DESC LIMIT %s OFFSET %s"
        cursor.execute(query, (size, offset))
        history = cursor.fetchall()
        cursor.close()
        conn.close()
        return history
    except Error as e:
        print(f"Error fetching shoot history with pagination: {str(e)}")
        return None

# Lưu lịch sử bắn
def save_shoot_history(username, status):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO history_shoot (username, status) VALUES (%s, %s)"
        cursor.execute(query, (username, status))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Error saving shoot history: {str(e)}")
        return False

# Lưu lịch sử phát hiện
def get_discovery_history(page, limit):
    try:
        offset = (page - 1) * limit
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM discovery_history ORDER BY time DESC LIMIT %s OFFSET %s"
        cursor.execute(query, (limit, offset))
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        return results
    except Exception as e:
        print(f"Lỗi truy vấn phân trang discovery_history: {e}")
        return None

#  luu lịch sử phát hiện
def save_discovery_history(method, distance):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "INSERT INTO discovery_history (method, distance) VALUES (%s, %s)"
        cursor.execute(query, (method, distance))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    except Error as e:
        print(f"Error inserting discovery history: {str(e)}")
        return False


#      lấy ra số đạn còn lại
def get_first_bullet():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        query = "SELECT * FROM bullet ORDER BY id ASC LIMIT 1"
        cursor.execute(query)
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        return result
    except mysql.connector.Error as e:
        print(f"Error fetching bullet: {str(e)}")
        return None























#  code ngày xưa
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


def get_total_discovery_history():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM discovery_history"
        cursor.execute(query)
        total = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return total
    except Error as e:
        print(f"Lỗi đếm tổng số bản ghi discovery_history: {str(e)}")
        return None

def get_total_shoot_history():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        query = "SELECT COUNT(*) FROM history_shoot"
        cursor.execute(query)
        total = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return total
    except Error as e:
        print(f"Lỗi đếm tổng số bản ghi history_shoot: {str(e)}")
        return None


# Trừ đạn
def decrease_bullet():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # Lấy số đạn hiện tại
        query = "SELECT * FROM bullet ORDER BY id ASC LIMIT 1"
        cursor.execute(query)
        current_bullet = cursor.fetchone()

        if current_bullet and current_bullet[1] > 0:  # Giả sử cột số lượng đạn là cột thứ 2
            # Trừ 1 viên đạn
            update_query = "UPDATE bullet SET number = number - 1 WHERE id = %s"
            cursor.execute(update_query, (current_bullet[0],))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        else:
            cursor.close()
            conn.close()
            return False
    except Error as e:
        print(f"Error decreasing bullet: {str(e)}")
        return False