#include <WiFi.h>
#include <ESP32Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <HTTPClient.h>

// 🟡 WiFi
const char* ssid = "Redmi";
const char* password = "12345678";
WiFiServer server(5000);
WiFiClient client;

// 🔵 LCD (I2C address thường là 0x27)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// 🟢 Servo quay hướng
Servo servoX, servoY;
const int servoXPin = 13;
const int servoYPin = 12;
int currentAngleX = 90;
int currentAngleY = 90;

// 🔴 Cảm biến siêu âm
#define TRIG_PIN 2
#define ECHO_PIN 4

// 🟠 Servo bắn
#define FIRE_SERVO_PIN 5
#define LED 14
Servo FireServo;

// 🟣 API kiểm tra lệnh bắn
const char* serverUrlfire = "http://192.168.83.239:5000/check_fire";

// ⏲️ Đọc cảm biến mỗi 5s
unsigned long lastDistanceReadTime = 0;
const unsigned long distanceReadInterval = 5000;

// 📩 Dữ liệu từ socket
String input = "";

void setup() {
  Wire.begin(21, 22);  // SDA=21, SCL=22
  lcd.init();
  lcd.backlight();
  lcd.setCursor(0, 0);
  lcd.print("ESP32 Dang ket noi");

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
  FireServo.write(0);  // ban đầu đóng

  // Cảm biến
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  // LED bắn
  pinMode(LED, OUTPUT);
  digitalWrite(LED, LOW);
}

// 📏 Đo khoảng cách
float readDistanceCM() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH, 25000);  // timeout 25ms
  float distance = duration * 0.034 / 2;
  return distance;
}

// 📌 Di chuyển servo mượt
void moveServoSmooth(Servo& servo, int& currentAngle, int targetAngle, int delayTime = 10) {
  int step = (targetAngle > currentAngle) ? 1 : -1;
  while (currentAngle != targetAngle) {
    currentAngle += step;
    servo.write(currentAngle);
    delay(delayTime);
  }
}

// 📡 Kiểm tra lệnh FIRE từ web
void checkCommandFromWeb() {
  HTTPClient http;
  http.begin(serverUrlfire);
  int httpResponseCode = http.GET();

  if (httpResponseCode > 0) {
    String response = http.getString();
    Serial.println("🔥 Phản hồi server: " + response);
    lcd.clear();
    lcd.setCursor(0, 0);

    if (response.indexOf("\"fire\":true") > -1 || response.indexOf("\"command\":\"fire\"") > -1) {
      lcd.print("FIRE!");
      FireServo.write(90);     // Bắn
      digitalWrite(LED, HIGH);
      delay(3000);             // Thời gian giữ servo mở
      FireServo.write(0);      // Thu lại
      digitalWrite(LED, LOW);
      lcd.clear();
      lcd.print("Ready again");
    } else {
      lcd.print("No command");
    }
  } else {
    Serial.print("❌ HTTP Error: ");
    Serial.println(httpResponseCode);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Web Error");
  }

  http.end();
}

void loop() {
  unsigned long currentTime = millis();

  // 🔁 Đọc khoảng cách định kỳ
  if (currentTime - lastDistanceReadTime >= distanceReadInterval) {
    lastDistanceReadTime = currentTime;

    float distance = readDistanceCM();
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Khoang cach:");
    lcd.setCursor(0, 1);
    lcd.print(distance, 1);
    lcd.print(" cm");

    Serial.print("📏 Khoảng cách: ");
    Serial.print(distance);
    Serial.println(" cm");
  }

  // 🌐 Kiểm tra lệnh bắn từ Web
  checkCommandFromWeb();

  // 📶 Xử lý kết nối từ client socket
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
        int commaIndex = input.indexOf(',');
        if (commaIndex != -1) {
          int offsetX = input.substring(0, commaIndex).toInt();
          int offsetY = input.substring(commaIndex + 1).toInt();

          int targetAngleX = 90 + (offsetX * 60.0 / 640.0);
          int targetAngleY = 90 + (offsetY * 60.0 / 480.0);
          targetAngleX = constrain(targetAngleX, 0, 180);
          targetAngleY = constrain(targetAngleY, 0, 180);

          Serial.printf("🎯 Goc X: %d | Y: %d\n", targetAngleX, targetAngleY);
          moveServoSmooth(servoX, currentAngleX, targetAngleX, 5);
          moveServoSmooth(servoY, currentAngleY, targetAngleY, 5);
        } else {
          Serial.println("⚠️ Dữ liệu socket không hợp lệ");
        }
        input = "";
      } else {
        input += c;
      }
    }
  }

  delay(300);  // Giảm tải và mượt hơn
}
