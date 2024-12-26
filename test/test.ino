#include <SPI.h>
#include <MFRC522.h>
#include <WiFi.h>
#include <HTTPClient.h>
#include <NTPClient.h>
#include <WiFiUdp.h>
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Keypad.h>
#include <ESP32Servo.h>

// Khởi tạo LCD1602 với địa chỉ I2C (thường là 0x27 hoặc 0x3F)
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Định nghĩa các hàng và cột của bàn phím 4x4
const byte ROW_NUM = 4;
const byte COLUMN_NUM = 4;
char keys[ROW_NUM][COLUMN_NUM] = {
  {'1', '2', '3', 'A'},
  {'4', '5', '6', 'B'},
  {'7', '8', '9', 'C'},
  {'*', '0', '#', 'D'}
};
byte pin_rows[ROW_NUM] = {33, 25, 26, 14};
byte pin_column[COLUMN_NUM] = {27, 13, 5, 4};
Keypad keypad = Keypad(makeKeymap(keys), pin_rows, pin_column, ROW_NUM, COLUMN_NUM);

// Chân kết nối RC522
#define SS_PIN 12
#define RST_PIN 15

MFRC522 rfid(SS_PIN, RST_PIN); // RC522 instance

// WiFi và Server
const char* ssid = "Redmi";
const char* password = "12345678";
const char* serverUrl = "http://192.168.149.85:3000/log_access";
const char* serverUrlpass = "http://192.168.149.85:3000/checkpass";
const char* serverUrltime = "http://192.168.149.85:3000/get-time";

// UDP để nhận tín hiệu từ ESP8266
WiFiUDP udp;
const int udpPort = 4210; // Cổng UDP lắng nghe
WiFiServer server(80);
int ok=1;

// NTP Client
WiFiUDP ntpUDP;
NTPClient timeClient(ntpUDP, "pool.ntp.org", 7 * 3600, 60000);
String inputString = "";

// Servo và LED
#define SERVO 2
Servo doorServo;
int LED = 32;

// Biến điều khiển mở cửa
bool openCommandReceived = false;
unsigned long openStartTime = 0;
const unsigned long openDuration = 5000;

void setup() {
    Serial.begin(115200);
    SPI.begin();
    rfid.PCD_Init();

    // Kết nối WiFi
    WiFi.begin(ssid, password);
    while (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        Serial.println("Connecting to WiFi...");
    }
    Serial.println("WiFi connected");
    Serial.print("ESP32 IP Address: ");
    Serial.println(WiFi.localIP());

    // Bắt đầu UDP
    udp.begin(udpPort);
    Serial.printf("Lắng nghe UDP trên cổng %d...\n", udpPort);

    // Khởi động NTP và các thiết bị khác
    timeClient.begin();
    doorServo.attach(SERVO);
    pinMode(LED, OUTPUT);
    lcd.init();
    lcd.backlight();
    lcd.setCursor(0, 0);
    lcd.print("Smart Door Ready");
}
void loop() {
    checkForUDP();
    timeClient.update(); // Cập nhật thời gian từ NTP
    
    if (isTimeValid()) {  // Kiểm tra nếu thời gian hợp lệ
        if(ok==0){
          lcd.clear();
          lcd.setCursor(0, 0);
          lcd.print("Smart Door Ready");
          ok=1;
        }
        if (rfid.PICC_IsNewCardPresent()) {
            Serial.println("Card present.");
            readRFID();
        }

        char key = keypad.getKey();
        if (key) {
            if (inputString == "") {
                lcd.clear();
            }
            lcd.setCursor(0, 0);
            lcd.print("Ban nhan phim:");

            if (key >= '0' && key <= '9') {
                lcd.setCursor(0, 1);
                inputString += key;
                lcd.print(inputString);
            } else if (key == '#') {
                checkpass(inputString);
                inputString = "";
            } else if (key == '*') {
                inputString = "";
                lcd.clear();
            }
        }
        checkFacialRecognition();

        if (openCommandReceived && (millis() - openStartTime < openDuration)) {
            doorServo.write(90); // Mở cửa
            digitalWrite(LED, HIGH); // Bật đèn LED khi cửa mở
        } else {
            doorServo.write(0); // Đóng cửa
            digitalWrite(LED, LOW); // Tắt đèn LED khi cửa đóng
            if (openCommandReceived) {
                lcd.clear();
                lcd.print("close door");
            }
            openCommandReceived = false;
        }
    } else {
        if (ok==1){
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Closed");
        ok=0;
        }
    }
}

void checkForUDP() {
    int packetSize = udp.parsePacket();
    if (packetSize) {
        char incomingPacket[255];
        int len = udp.read(incomingPacket, 255);
        if (len > 0) {
            incomingPacket[len] = '\0';
        }
        String message = String(incomingPacket);
        Serial.printf("UDP nhận được: %s\n", message.c_str());

        // Kiểm tra tín hiệu mở cửa
        if (message == "OPEN_DOOR") {
            Serial.println("Tín hiệu mở cửa từ ESP8266!");
            lcd.clear();
            lcd.print("Gas Alert! Open!");
            doorServo.write(90); // Mở cửa (90 độ)
            digitalWrite(LED, HIGH); // Bật đèn LED khi cửa mở
            Serial.println("LED ON");
            delay(5000); // Giữ cửa mở trong 5 giây
            doorServo.write(0); // Đóng cửa
            digitalWrite(LED, LOW); // Tắt đèn LED khi cửa đóng
            lcd.clear();
            lcd.print("close door");
            openCommandReceived = true;
            openStartTime = millis();
        }
    }
}

// Hàm kiểm tra xem thời gian có hợp lệ hay không
bool isTimeValid() {
    timeClient.update();
    int hour = timeClient.getHours();
    int minute = timeClient.getMinutes();

    HTTPClient http;
    http.begin(serverUrltime);  // Địa chỉ API
    int httpResponseCode = http.GET();
    
    if (httpResponseCode > 0) {
      String payload = http.getString();
      Serial.println(payload);  // In ra dữ liệu nhận được từ server
      // Phân tích JSON
      int openTimeStart = payload.indexOf("\"openTime\":\"") + 12;  // Bắt đầu từ sau chuỗi "openTime":" 
        int openTimeEnd = payload.indexOf("\"", openTimeStart);  // Kết thúc khi gặp dấu "
        String openTime = payload.substring(openTimeStart, openTimeEnd);  // Lấy openTime từ payload

        int closeTimeStart = payload.indexOf("\"closeTime\":\"") + 13;  // Bắt đầu từ sau chuỗi "closeTime":" 
        int closeTimeEnd = payload.indexOf("\"", closeTimeStart);  // Kết thúc khi gặp dấu "
        String closeTime = payload.substring(closeTimeStart, closeTimeEnd);  // Lấy closeTime từ payload

        // Tách giờ và phút từ chuỗi thời gian
        int openHour = openTime.substring(0, 2).toInt();  // Lấy giờ mở
        int openMinute = openTime.substring(3, 5).toInt();  // Lấy phút mở

        int closeHour = closeTime.substring(0, 2).toInt();  // Lấy giờ đóng
        int closeMinute = closeTime.substring(3, 5).toInt();

        // Kiểm tra nếu thời gian nằm trong khoảng mở và đóng cửa
        if ((hour > openHour || (hour == openHour && minute >= openMinute)) &&
            (hour < closeHour || (hour == closeHour && minute < closeMinute))) {
            return true;  // Thời gian hợp lệ
        }
    } else {
        Serial.println("Error on HTTP request");
        if ((hour == 23 && minute >= 30) || (hour >= 0 && hour < 5)) {
            return false;  // Không hợp lệ trong khoảng thời gian này
        }
        return true; 
    }

    http.end();  // Kết thúc HTTP request

    return false; 
}

void readRFID() {
    Serial.println("Waiting for RFID card...");
    rfid.PICC_ReadCardSerial();
    
    String uidString = "";
    for (byte i = 0; i < rfid.uid.size; i++) {
        uidString += String(rfid.uid.uidByte[i]) + (i < rfid.uid.size - 1 ? " " : "");
    }
    
    Serial.println("Scanned UID: " + uidString);
    
    // Gửi dữ liệu lên server
    sendToServer(uidString);
    
    // Halt PICC
    rfid.PICC_HaltA();
    rfid.PCD_StopCrypto1();
    
}
void checkpass(String keyword) {
    WiFiClient client;  // Tạo một đối tượng WiFiClient
    HTTPClient http;    // Tạo một đối tượng HTTPClient
    http.begin(client, serverUrlpass); // Bắt đầu HTTP request với WiFiClient
    Serial.println(keyword); 
    http.addHeader("Content-Type", "application/json"); // Đặt tiêu đề
    String payload = "{\"keyword\":\"" + keyword + "\"}"; // Tạo payload JSON
    int httpResponseCode = http.POST(payload); // Gửi dữ liệu

    if (httpResponseCode > 0) {
        String response = http.getString(); // Nhận phản hồi từ server
        Serial.println(httpResponseCode); // In ra mã phản hồi
        Serial.println(response); // In ra nội dung phản hồi

        // Hiển thị trên LCD
        lcd.clear();
        lcd.setCursor(0, 0);

        if (response.indexOf("\"doorStatus\":1") > -1) {
                lcd.print("Open : Success");
                 doorServo.write(90); // Mở cửa (90 độ)
                  digitalWrite(LED, HIGH); // Bật đèn LED khi cửa mở
                  Serial.println("LED ON");
                delay(5000); // Giữ cửa mở trong 5 giây
                doorServo.write(0); // Đóng cửa
                digitalWrite(LED, LOW); // Tắt đèn LED khi cửa đóng
                lcd.clear();
                lcd.print("close door");

            } else {
                lcd.print("Access: Failure");
            }
    } else {
        Serial.print("Error on sending POST: ");
        Serial.println(httpResponseCode);
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Connection Error");
    }
}

void checkFacialRecognition() {
    WiFiClient client = server.available();
    if (client) {
        Serial.println("Nhận khuôn mặt thành công");
        while (client.connected()) {
            if (client.available()) {
                String command = client.readStringUntil('\n');
                command.trim();
                if (command == "open") {
                    lcd.clear();
                    lcd.print("Open : Success");
                    openCommandReceived = true;
                    openStartTime = millis();
                }
            }
        }
        client.stop();
        Serial.println("Client disconnected");
    }
}

void sendToServer(String uid) {
    if (WiFi.status() == WL_CONNECTED) {
        WiFiClient client;  // Tạo một đối tượng WiFiClient
        HTTPClient http;    // Tạo một đối tượng HTTPClient
        http.begin(client, serverUrl); // Bắt đầu HTTP request với WiFiClient

        http.addHeader("Content-Type", "application/json"); // Đặt tiêu đề

        // Tạo dữ liệu JSON
        String timeString = timeClient.getFormattedTime(); // Lấy thời gian từ NTP
        String jsonData = "{\"userID\":\"" + uid + "\", \"time\":\"" + timeString + "\"}";

        int httpResponseCode = http.POST(jsonData); // Gửi dữ liệu

        if (httpResponseCode > 0) {
            String response = http.getString(); // Nhận phản hồi từ server
            Serial.println(httpResponseCode); // In ra mã phản hồi
            Serial.println(response); // In ra nội dung phản hồi

            // Hiển thị trên LCD
            lcd.clear();
            lcd.setCursor(0, 0);

            if (response.indexOf("\"doorStatus\":1") > -1) {
                lcd.print("Open : Success");
                 doorServo.write(90); // Mở cửa
                 digitalWrite(LED, HIGH); // Bật đèn LED khi cửa mở
                 Serial.println("LED ON");
                delay(5000); // Giữ cửa mở trong 5 giây
                doorServo.write(0); // Đóng cửa
                digitalWrite(LED, LOW); // Tắt đèn LED khi cửa đóng
                lcd.clear();
                lcd.print("close door");
                
            } else {
                lcd.print("Access: Failure");
            }
            lcd.setCursor(0, 1);
            lcd.print("ID: ");
            lcd.print(uid);
        } else {
            Serial.print("Error on sending POST: ");
            Serial.println(httpResponseCode);
            lcd.clear();
            lcd.setCursor(0, 0);
            lcd.print("Connection Error");
        }

        http.end(); // Kết thúc HTTP request
    } else {
        Serial.println("WiFi Disconnected");
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("WiFi Disconnected");
    }
}