import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os

# Thông tin gửi email
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "pvt1213.phamvantu@gmail.com"
EMAIL_PASSWORD = "movnbpvotcidvrym"

def send_email_with_image(to_email, subject, body, image_path):
    try:
        # Tạo nội dung email
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = to_email
        msg['Subject'] = subject

        # Thêm nội dung văn bản
        msg.attach(MIMEText(body, 'plain'))

        # Đính kèm hình ảnh
        if os.path.exists(image_path):  # Kiểm tra hình ảnh có tồn tại không
            with open(image_path, 'rb') as img:
                mime_image = MIMEImage(img.read())
                mime_image.add_header('Content-Disposition', 'attachment', filename=os.path.basename(image_path))
                msg.attach(mime_image)
        else:
            print(f"Hình ảnh không tồn tại: {image_path}")

        # Kết nối tới server SMTP
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()  # Kích hoạt mã hóa bảo mật
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.send_message(msg)
            print(f"Email đã được gửi tới {to_email}")
    except Exception as e:
        print(f"Không thể gửi email: {e}")

# # Gửi email
# send_email_with_image(
#     to_email="tutupham5@gmail.com",  # Địa chỉ người nhận
#     subject="Đây là email gửi đến phamtu",                 # Chủ đề email
#     body=" Xin chào bạn , nhà bạn đang có người cố gắng xâm nhập trái phép . Đây là hình ảnh của họ . ",  # Nội dung email
#     image_path= "D:\phamtuTest\emotion\images.jpg"     # Đường dẫn tới hình ảnh
# )
