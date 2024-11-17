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
byte pin_rows[ROW_NUM] = {33, 25, 26, 14}; // Chân hàng của bàn phím
byte pin_column[COLUMN_NUM] = {27, 13, 5, 4}; // Chân cột của bàn phím

Keypad keypad = Keypad(makeKeymap(keys), pin_rows, pin_column, ROW_NUM, COLUMN_NUM);

// Chân kết nối RC522
#define SS_PIN 12
#define RST_PIN 15

MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class

const char* ssid = "phamtuu"; // Thay đổi với SSID của bạn
const char* password = "123456789"; // Thay đổi với mật khẩu WiFi của bạn
const char* serverUrl = "http://192.168.226.239:3000/log_access"; // Địa chỉ IP máy chủ
const char* serverUrlpass = "http://192.168.226.239:3000/checkpass"; // Địa chỉ IP máy chủ

String inputString = "";

WiFiUDP udp; // Tạo đối tượng UDP
NTPClient timeClient(udp, "pool.ntp.org", 7 * 3600, 60000); // Cấu hình NTP Client (UTC+7)

// Định nghĩa chân servo và khởi tạo đối tượng Servo
#define SERVO 2
Servo doorServo;

// Định nghĩa chân LED
int LED = 32;



float previousTemperature = NAN;

// Server for facial recognition  nhan dien mat  mo cua 
WiFiServer server(80);
bool openCommandReceived = false;
unsigned long openStartTime = 0;
const unsigned long openDuration = 5000;


void setup() {
    Serial.begin(115200);
    SPI.begin(); // (SCK, MISO, MOSI, SS)
    rfid.PCD_Init(); // Init MFRC522
    WiFi.begin(ssid, password); // Kết nối WiFi

    doorServo.attach(SERVO);

     // Khởi tạo chân LED
    pinMode(LED, OUTPUT);
    
    digitalWrite(LED, LOW); // Tắt đèn LED lúc bắt đầu
   


    while (WiFi.status() != WL_CONNECTED) {
        delay(5000);
        Serial.println("Connecting to WiFi...");
    }

    Serial.println("Connected to WiFi");

     // In địa chỉ IP của ESP32
    Serial.print("ESP32 IP Address: ");
    Serial.println(WiFi.localIP()); // In địa chỉ IP ra Serial Monitor

    server.begin();
    timeClient.begin(); // Bắt đầu NTP client
  
    lcd.init(); // Khởi động LCD
    lcd.backlight(); // Bật đèn nền LCD
    lcd.setCursor(0, 0);
    lcd.print("Smart Door Ready");

  
  
}

void loop() {
    timeClient.update(); // Cập nhật thời gian từ NTP
    if (rfid.PICC_IsNewCardPresent()) {
        Serial.println("Card present."); // Thêm dòng này để kiểm tra
        readRFID();
    }

     
    char key = keypad.getKey();
      if (key) {
        if(inputString == ""){
          lcd.clear();
        }
        lcd.setCursor(0, 0);
        lcd.print("Ban nhan phim:");
       
        // Thêm phím vào chuỗi nhập vào
        if (key >= '0' && key <= '9') {
          lcd.setCursor(0, 1);
          inputString += key; // Chỉ thêm nếu là số
           lcd.print(inputString);
          for (int i = 0; i < inputString.length(); i++) {
            // lcd.print("*");
          }
        } else if (key == '#') {
            checkpass(inputString); // Gọi hàm check
            inputString = ""; // Reset chuỗi nhập vào sau khi kiểm tra
        } else if (key == '*') {
          inputString = "";
          lcd.clear();
        }
      }
      checkFacialRecognition();

      if (openCommandReceived && (millis() - openStartTime < openDuration)) {
        doorServo.write(90); // Open door
          digitalWrite(LED, HIGH); // Bật đèn LED khi cửa mở
      } else {
        doorServo.write(0); // Close door
         digitalWrite(LED, LOW); // Tắt đèn LED khi cửa đóng
         if (openCommandReceived){
          lcd.clear();
          lcd.print("close door");
         }
        openCommandReceived = false;
      }

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
