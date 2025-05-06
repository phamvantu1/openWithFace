#include <WiFi.h>
#include <ESP32Servo.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <HTTPClient.h>
#include <WebSocketsServer.h>
#include <ArduinoJson.h>

// Khởi tạo WebSocket server
WebSocketsServer webSocket = WebSocketsServer(8080);


// Khởi tạo LCD1602 với địa chỉ I2C (thường là 0x27 hoặc 0x3F)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// 🟡 WiFi
const char* ssid = "phamtuu";
const char* password = "123456789";
WiFiServer server(5000);
WiFiClient client;

// Định nghĩa chân servo và khởi tạo đối tượng Servo bắn
#define SERVO 5
Servo doorServo;


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

// còi
#define SIREN_PIN 19  // Chân GPIO điều khiển transistor

unsigned long lastMoveTime = 0;  // Thời gian chuyển động cuối cùng

unsigned long lastObjectDetectedTime = 0;
bool isObjectDetected = false;  // Biến để theo dõi việc phát hiện vật

unsigned long openStartTime = 0;
const unsigned long openDuration = 3000;
bool openCommandReceived = false;


bool checkOpenRadar = false;

bool checkNapDanThanhCong = false;


unsigned long lastDistanceTime = 0;
int currentDistance = 0;


Servo servoScan;
const int servoScanPin = 27; // Chọn 1 chân digital chưa dùng
int ultrasonicDistance;

// 📩 Dữ liệu từ socket
String input = "";
bool isFiring = false;


unsigned long lastRadarScan = 0;
const unsigned long radarInterval = 50; // ms
int scanAngle = 0;
bool increasing = true;

void handleRadarScan() {
    if (millis() - lastRadarScan >= radarInterval && checkOpenRadar) {
        lastRadarScan = millis();
        servoScan.write(scanAngle);
        delay(1000); //  cho delay 1s để gửi cho fe , tránh gửi liên tục
        int distance = calculateDistance();
        sendRadarData(scanAngle, distance);

        // //  Nếu phát hiện vật ở gần (dưới 20cm), quay trục X đến hướng đó
        // if (distance > 0 && distance < 20) {
        //     Serial.printf("📍 Vật ở gần tại góc %d, khoảng cách: %d cm\n", scanAngle, distance);
        //     moveServoSmooth(servoX, currentAngleX, scanAngle);
        // }

        if (increasing) {
            scanAngle += 5;
            if (scanAngle >= 180) increasing = false;
        } else {
            scanAngle -= 5;
            if (scanAngle <= 0) increasing = true;
        }
    }
}


// Hàm xử lý sự kiện WebSocket
void webSocketEvent(uint8_t num, WStype_t type, uint8_t * payload, size_t length) {
    switch(type) {
        case WStype_DISCONNECTED:
            Serial.printf("[%u] Disconnected!\n", num);
            break;
        case WStype_CONNECTED:
            Serial.printf("[%u] Connected!\n", num);
            break;
        case WStype_TEXT:


            Serial.printf("[%u] Received text: %s\n", num, payload);

              // Tạo bộ phân tích JSON
            StaticJsonDocument<200> doc;
            DeserializationError error = deserializeJson(doc, payload);

            if (error) {
                Serial.print(F("❌ Lỗi phân tích JSON: "));
                Serial.println(error.f_str());
                return;
            }

            String command = doc["command"];  // Lấy giá trị của khóa "command"
            Serial.printf("📩 Lệnh nhận được: %s\n", command.c_str());

            if (command == "ArrowUp") {
                Serial.println("Arduino: Di chuyển lên");
                // Di chuyển servoY lên (giảm góc)
                int newAngleY = currentAngleY - 10;
                newAngleY = constrain(newAngleY, 0, 180);
                moveServoSmooth(servoY, currentAngleY, newAngleY);
            }
            else if (command == "ArrowDown") {
                 Serial.println("Arduino: Di chuyển xuống");
                // Di chuyển servoY xuống (tăng góc)
                int newAngleY = currentAngleY + 10;
                newAngleY = constrain(newAngleY, 0, 180);
                moveServoSmooth(servoY, currentAngleY, newAngleY);
            }
            else if (command == "ArrowLeft") {
                Serial.println("Arduino: Di chuyển sang trái");
                // Di chuyển servoX sang trái (giảm góc)
                int newAngleX = currentAngleX - 10;
                newAngleX = constrain(newAngleX, 0, 180);
                moveServoSmooth(servoX, currentAngleX, newAngleX);
            }
            else if (command == "ArrowRight") {
                Serial.println("Arduino: Di chuyển sang phải");
                // Di chuyển servoX sang phải (tăng góc)
                int newAngleX = currentAngleX + 10;
                newAngleX = constrain(newAngleX, 0, 180);
                moveServoSmooth(servoX, currentAngleX, newAngleX);
            } 
            else if (command == "Space") {
                Serial.println("Arduino: Bắn");
                // Xử lý bắn
                openCommandReceived = true;
                openStartTime = millis();
            }
            else if (command == "open_radar") {
                Serial.println("Arduino: mở radar");
                // Xử lý radar
                checkOpenRadar = true;

            }else if (command == "close_radar") {
                Serial.println("Arduino: đóng radar");
                // Xử lý radar
                checkOpenRadar = false;

            }
            else if (command == "reload") {
                Serial.println("Arduino: nạp đạn thành công");
                // Xử lý nạp đạn
                checkNapDanThanhCong = true;

            }
            else if (command == "STOP") {
                Serial.println("Arduino: Dừng di chuyển");
                // Không cần xử lý gì thêm vì servo sẽ giữ nguyên vị trí
            }
            break;
    }
}

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

    // Khởi tạo WebSocket
    webSocket.begin();
    webSocket.onEvent(webSocketEvent);
    Serial.println("WebSocket server started");

    // Servo setup
    servoX.attach(servoXPin);
    servoY.attach(servoYPin);
    FireServo.attach(FIRE_SERVO_PIN);
    servoX.write(currentAngleX);
    servoY.write(currentAngleY);
    FireServo.write(0);  // Ban đầu đóng

    // servo cho  bắn
    doorServo.attach(SERVO);

    // Cảm biến
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);

    // LED
    pinMode(LED, OUTPUT);
    digitalWrite(LED, LOW);

    // còi
    pinMode(SIREN_PIN, OUTPUT);
    digitalWrite(SIREN_PIN, LOW);  // Bắt đầu với còi tắt

    lcd.init(); // Khởi động LCD
    lcd.clear();
    lcd.backlight(); // Bật đèn nền LCD
    // Hiển thị chuỗi dài trên LCD
    String longText = "    san sang       chien dau !!!";
    displayLongText(longText);

    Serial.println("LCD Displayed");


    servoScan.attach(servoScanPin); // Gắn servo quét


}



void displayLongText(String text) {
    lcd.clear();
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


// Cấu trúc JSON để gửi thông tin về khoảng cách và góc
void sendRadarData(int angle, int distance) {
    // Tạo đối tượng JSON
    StaticJsonDocument<200> doc;
    doc["radar"]["goc"] = angle;
    doc["radar"]["kc"] = distance;

    // Chuyển đối tượng JSON thành chuỗi
    String output;
    serializeJson(doc, output);

    // Gửi dữ liệu qua WebSocket
    // webSocket.sendTXT(0, output);  // 0 là chỉ số của client (điều chỉnh nếu có nhiều client)

    webSocket.broadcastTXT(output);

    // In ra console để kiểm tra
    Serial.println(output);

}

// gửi biến cờ sang cho fe để check bắn thành công hay thất bại
void sendCheckSuccess(bool checkFiringStatus) {
    // Tạo đối tượng JSON
    StaticJsonDocument<100> doc;
    doc["checkFiringStatus"] = checkFiringStatus;

    // Chuyển đối tượng JSON thành chuỗi
    String output;
    serializeJson(doc, output);

    // Gửi qua WebSocket
    webSocket.broadcastTXT(output);

    // In ra Serial để debug
    Serial.println(output);
}


// Đo khoảng cách (có timeout tránh block hệ thống)
int calculateDistance() {
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  long duration = pulseIn(ECHO_PIN, HIGH, 20000); // Timeout 20ms (tương đương ~3.4m)

  if (duration == 0) return -1; // Không đo được

  int distance = duration * 0.034 / 2;
  return distance;
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


    // Xử lý WebSocket
    webSocket.loop();

    if (client && client.connected()) {
        while (client.available()) {
            char c = client.read();
            if (c == '\n') {
                input.trim();
                  if (input == "open") {
                      openCommandReceived = true;
                      openStartTime = millis();
                  } else  if (input.length() > 2 && input.indexOf(',') != -1) {
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


                      String longText = "   Phat hien ke      dich";
                      displayLongText(longText);

                      digitalWrite(LED, HIGH); // Bật đèn LED khi chuyen dong

                          if (abs(targetAngleX - currentAngleX) > 1) {
                              moveServoSmooth(servoX, currentAngleX, targetAngleX);
                          }
                          if (abs(targetAngleY - currentAngleY) > 1) {
                              moveServoSmooth(servoY, currentAngleY, targetAngleY);
                          }

                      currentAngleX = targetAngleX;
                      currentAngleY = targetAngleY;

                      lastMoveTime = millis();  // Cập nhật thời gian khi có chuyển động
                      lastObjectDetectedTime = currentTime; // Cập nhật thời gian phát hiện vật
                      isObjectDetected = true;  // Đánh dấu đã phát hiện vật

                  }else {
                          Serial.println("⚠️ Dữ liệu socket không hợp lệ: " + input);
                        }
                  input = "";
            } else {
                input += c;
              }
        }
    }



        // Nếu không phát hiện vật trong 10 giây, tắt đèn và hiển thị "Không phát hiện vật"
        if (isObjectDetected && currentTime - lastObjectDetectedTime > 10000) {
            digitalWrite(LED, LOW);  // Tắt đèn LED
            String noDetectionText = "Khong phat hien      ke dich";
            displayLongText(noDetectionText);  // Cập nhật LCD với thông báo "Không phát hiện vật"
            isObjectDetected = false;  // Đánh dấu không còn phát hiện vật
        }


        // còi kêu
        if (isObjectDetected) {
            for (int i = 0; i < 3; i++) {
                digitalWrite(SIREN_PIN, HIGH);  // Bật còi
                delay(250);                     // Chờ 250ms
                digitalWrite(SIREN_PIN, LOW);   // Tắt còi
                delay(250);                     // Chờ 250ms
            }
        } else {
            digitalWrite(SIREN_PIN, LOW);       // Đảm bảo tắt còi nếu không phát hiện
        }

        // xử lý bắn
        if (openCommandReceived && checkNapDanThanhCong ){
                // doorServo.write(0); // Open súng

                sendCheckSuccess(true);
                Serial.println("Bắn thành công");

                String longText = " Ban thanh cong   ";
                displayLongText(longText);
                doorServo.write(0); // Open súng
                delay(2000);
                // bắn thành công rồi thì coi như hết đạn 
                checkNapDanThanhCong = false;
                openCommandReceived = false;
                // doorServo.write(90);
        }else if (openCommandReceived &&  !checkNapDanThanhCong){
          sendCheckSuccess(false);
          String longText = "  Khong co dan  ";
                displayLongText(longText);
                Serial.println("không có đạn để bắn");
                // không bắn được thì set lại thôi
                openCommandReceived = false;
        } else if (!openCommandReceived) {
            doorServo.write(90); // Close súng nếu không còn lệnh bắn
        }


      // xử lý radar quét
      if ( checkOpenRadar ){
        handleRadarScan();
      }



}