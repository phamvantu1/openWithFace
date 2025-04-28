#include <WiFi.h>
#include <ESP32Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <HTTPClient.h>


// Khởi tạo LCD1602 với địa chỉ I2C (thường là 0x27 hoặc 0x3F)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// 🟡 WiFi
const char* ssid = "phamtuu";
const char* password = "123456789";
WiFiServer server(5000);
WiFiClient client;


// 🟢 Servo quay hướng
Servo servoX, servoY;
const int servoXPin = 13;
const int servoYPin = 33;
int currentAngleX = 90;
int currentAngleY = 60;

// 🔴 Cảm biến siêu âm
#define TRIG_PIN 2
#define ECHO_PIN 4

// 🟠 Servo bắn
#define FIRE_SERVO_PIN 5
#define LED 14
Servo FireServo;

// 🟣 API kiểm tra lệnh bắn
const char* serverUrlfire = "http://192.168.83.239:5000/check_fire";

// ⏲️ Đọc cảm biến và HTTP định kỳ
unsigned long lastDistanceReadTime = 0;
unsigned long lastHttpCheckTime = 0;
unsigned long fireStartTime = 0;
const unsigned long distanceReadInterval = 5000;  // 5s
const unsigned long httpCheckInterval = 2000;     // 2s
const unsigned long fireDuration = 3000;          // 3s cho servo bắn

// 📩 Dữ liệu từ socket
String input = "";
bool isFiring = false;

void setup() {


    Serial.begin(115200);

    // WiFi setup
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }
    Serial.println("\n✅ WiFi connected");
    Serial.println(WiFi.localIP());
    server.begin();

    // Servo setup
    servoX.attach(servoXPin);
    servoY.attach(servoYPin);
    FireServo.attach(FIRE_SERVO_PIN);
    servoX.write(currentAngleX);
    servoY.write(currentAngleY);
    FireServo.write(0);  // Ban đầu đóng

    // Cảm biến
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);

    // LED bắn
    pinMode(LED, OUTPUT);
    digitalWrite(LED, LOW);

    lcd.init(); // Khởi động LCD
    lcd.clear();
    lcd.backlight(); // Bật đèn nền LCD
    // Hiển thị chuỗi dài trên LCD
    String longText = "    san sang       chien dau !!!";
    displayLongText(longText);

    Serial.println("LCD Displayed");

}

void displayLongText(String text) {
    int maxLength = 16;  // Mỗi dòng LCD có tối đa 16 ký tự
    int textLength = text.length();
    
    // Vòng lặp qua từng phần của chuỗi
    for (int i = 0; i < textLength; i += maxLength) {
        String part = text.substring(i, i + maxLength); // Cắt chuỗi thành đoạn con
        lcd.setCursor(0, i / maxLength);  // Di chuyển con trỏ đến dòng tiếp theo
        lcd.print(part);  // In phần của chuỗi vào LCD
    }
}

// 📏 Đo khoảng cách
float readDistanceCM() {
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    long duration = pulseIn(ECHO_PIN, HIGH, 10000); // Giảm timeout xuống 10ms
    float distance = duration * 0.034 / 2;
    return duration > 0 ? distance : -1; // Trả về -1 nếu lỗi
}

// 📌 Di chuyển servo mượt
void moveServoSmooth(Servo& servo, int& currentAngle, int targetAngle) {
    int step = (targetAngle > currentAngle) ? 2 : -2; // Tăng bước lên 5
    while (abs(currentAngle - targetAngle) > 1) {
        currentAngle += step;
        servo.write(currentAngle);
        delay(1); // Giảm delay xuống 1ms
    }
    currentAngle = targetAngle;
    servo.write(currentAngle);
}



void loop() {
    unsigned long currentTime = millis();

    // 📶 Xử lý kết nối từ client socket (ưu tiên)
    if (!client || !client.connected()) {
        client = server.available();
        if (client) {
            Serial.println("🖥️ Client da ket noi");
            input = "";
        }
    }

    if (client && client.connected()) {
        while (client.available()) {
            char c = client.read();
            if (c == '\n') {
                input.trim();
                if (input.length() > 2 && input.indexOf(',') != -1) {
                    Serial.printf("🕒 Nhận lúc: %lu ms\n", millis());
                    int commaIndex = input.indexOf(',');
                    int offsetX = input.substring(0, commaIndex).toInt();
                    int offsetY = input.substring(commaIndex + 1).toInt();

                    // Hiệu chỉnh dựa trên FOV (60° ngang, 45° dọc)
                    int targetAngleX = currentAngleX + (offsetX * 60.0 / 640.0);
                    int targetAngleY = currentAngleY + (offsetY * 45.0 / 480.0);

                    targetAngleX = constrain(targetAngleX, 0, 180);
                    targetAngleY = constrain(targetAngleY, 0, 180);

                    Serial.printf("🎯 Offset X: %d, Y: %d | Goc X: %d, Y: %d\n", offsetX, offsetY, targetAngleX, targetAngleY);

                    lcd.print("xin chao anh tu");

                    if (abs(targetAngleX - currentAngleX) > 1) {
                        moveServoSmooth(servoX, currentAngleX, targetAngleX);
                    }
                    if (abs(targetAngleY - currentAngleY) > 1) {
                        moveServoSmooth(servoY, currentAngleY, targetAngleY);
                    }

                    currentAngleX = targetAngleX;
                    currentAngleY = targetAngleY;
                } else {
                    Serial.println("⚠️ Dữ liệu socket không hợp lệ: " + input);
                }
                input = "";
            } else {
                input += c;
            }
        }
    }



}