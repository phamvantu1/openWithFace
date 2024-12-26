#include <DHT.h>
#include <ESP8266WiFi.h>
#include <WiFiUdp.h>

#define DHTPIN D4                // Pin kết nối với DHT11
#define DHTTYPE DHT11            // Loại cảm biến DHT11
#define LED_PIN D2               // Pin LED cho nhiệt độ và độ ẩm
#define LDR_PIN A0               // Pin cho quang trở (LDR)
#define LED_LIGHT_PIN D5         // Pin LED để bật khi trời tối
#define GAS_SENSOR_PIN D6        // Pin cho cảm biến khí gas
#define LED_GAS_PIN D7           // Pin LED cảnh báo khí gas

const float TEMP_THRESHOLD = 30.0;  // Ngưỡng nhiệt độ
const int GAS_THRESHOLD = 300;      // Ngưỡng khí gas để gửi cảnh báo

// Thông tin WiFi
const char* ssid = "Redmi";        // Tên WiFi của bạn
const char* password = "12345678"; // Mật khẩu WiFi của bạn

// UDP cấu hình
WiFiUDP udp;
const char* esp32IP = "192.168.149.153"; // Địa chỉ IP của ESP32
const int udpPort = 4210;             // Cổng UDP

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();

  pinMode(LED_PIN, OUTPUT);
  pinMode(LED_GAS_PIN, OUTPUT);

  digitalWrite(LED_PIN, LOW);
  digitalWrite(LED_GAS_PIN, LOW);

  // Kết nối WiFi
  WiFi.begin(ssid, password);
  Serial.print("Đang kết nối WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println("\nWiFi đã kết nối!");
  Serial.print("Địa chỉ IP ESP8266: ");
  Serial.println(WiFi.localIP());

  // Bắt đầu UDP
  udp.begin(4210);
  Serial.println("UDP client đã sẵn sàng.");
}

void loop() {
  // Đọc dữ liệu từ cảm biến
  float temperature = dht.readTemperature();
  int gasLevel = analogRead(GAS_SENSOR_PIN);

  // Kiểm tra lỗi khi đọc cảm biến
  if (isnan(temperature)) {
    Serial.println("Không đọc được nhiệt độ từ DHT11");
    return;
  }

  // In dữ liệu
  Serial.print("Nhiệt độ: ");
  Serial.println(temperature);
  Serial.print("Mức khí gas: ");
  Serial.println(gasLevel);

  // Kiểm tra khí gas
  if (gasLevel > GAS_THRESHOLD) {
    Serial.println("Cảnh báo: Khí gas vượt ngưỡng an toàn!");

    // Bật LED cảnh báo
    digitalWrite(LED_GAS_PIN, HIGH);

    // Gửi tín hiệu mở cửa đến ESP32 qua UDP
    udp.beginPacket(esp32IP, udpPort);
    udp.print("OPEN_DOOR");
    udp.endPacket();
    Serial.println("Đã gửi tín hiệu mở cửa đến ESP32.");

    delay(5000);  // Chỉ gửi tín hiệu mỗi 5 giây để tránh spam
  } else {
    digitalWrite(LED_GAS_PIN, LOW);
  }

  delay(2000); // Đọc lại dữ liệu mỗi 2 giây
}
