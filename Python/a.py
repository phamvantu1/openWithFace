#  gui email port 5000
@app.route('/send-email', methods=['POST'])
def send_email():
    
    subject = "Đây là email cảnh báo có người đột nhập"
    body = "Ai đó đang muốn mở cửa nhà của bạn. Đây là hình ảnh của họ."
    image_path = "http://192.168.102.30/cam-lo.jpg"

    
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor(dictionary=True)
  
    try:
            # Save the image upon successful password verification
        image_path = downloadImageAndSave('http://192.168.102.30/cam-lo.jpg')

        # Save the action into the database
        action_query = """
            INSERT INTO action (card_number, action_type, status, image)
            VALUES (%s, %s, %s, %s)
        """
        action_values = ("", "", "FAILURE", image_path)
        cursor.execute(action_query, action_values)
        connection.commit()
        
        query = "SELECT email FROM user_iot WHERE email IS NOT NULL"
        cursor.execute(query)
        emails = cursor.fetchall()
        

        # Iterate through the list of email dictionaries
        for email_dict in emails:
            if 'email' in email_dict:  # Ensure the dictionary contains the key 'email'
                recipient_email = email_dict['email']
                try:
                    result = send_email_with_image(recipient_email, subject, body, image_path)
                    print(f"Email sent to {recipient_email}: {result}")
                    time.sleep(1)
                except Exception as e:
                    print(f"Failed to send email to {recipient_email}: {e}")

            print('Data saved to action table with image.')
            

    except Error as e:
        print("Database query or connection error:", e)
    
    
    return jsonify({"message": "result"})