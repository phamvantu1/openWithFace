#include <WiFi.h>
#include <ESP32Servo.h>

#define SERVO 13

// Update these with values suitable for your network.
const char* ssid = "Lan Anh";
const char* password = "244466666";

WiFiServer server(80);

Servo myServo;

bool openCommandReceived = false;
unsigned long openStartTime = 0;
const unsigned long openDuration = 15000; // Thời gian mở cửa (milliseconds)

void setup() {
  Serial.begin(115200);

  myServo.attach(SERVO);

  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Connected to WiFi");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  server.begin();
}

void loop() {
  WiFiClient client = server.available();

  if (client) {
    Serial.println("Nhận khuôn mặt thành công");

    while (client.connected()) {
      if (client.available()) {
        String command = client.readStringUntil('\n');
        command.trim();
        if (command == "open") {
          openCommandReceived = true;
          openStartTime = millis(); // Lưu thời gian khi nhận lệnh mở cửa
        }
      }
    }
    client.stop();
    Serial.println("Client disconnected");
  }

  // Kiểm tra nếu đã nhận lệnh mở cửa và chưa hết thời gian mở
  if (openCommandReceived && (millis() - openStartTime < openDuration)) {
    myServo.write(90); // Mở cửa
  } else {
    myServo.write(0); // Đóng cửa
    openCommandReceived = false; // Đặt lại biến cờ
  }
}
