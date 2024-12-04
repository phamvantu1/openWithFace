#include <DHT.h>
#include <ESP8266WiFi.h>

// WiFi thông tin
const char* ssid = "phamtuu";  // Thay bằng tên mạng WiFi của bạn
const char* password = "123456789";  // Thay bằng mật khẩu WiFi của bạn

#define DHTPIN D4                // Pin kết nối với DHT11
#define DHTTYPE DHT11            // Loại cảm biến DHT11
#define LED_PIN D2               // Pin LED cho nhiệt độ và độ ẩm
#define LDR_PIN A0               // Pin cho quang trở (LDR)
#define LED_LIGHT_PIN D5         // Pin LED để bật khi trời tối
#define LED_NHAC D8

const float TEMP_THRESHOLD = 30.0;  // Ngưỡng nhiệt độ để bật LED
const float HUM_THRESHOLD = 70.0;   // Ngưỡng độ ẩm để bật LED
const int LIGHT_THRESHOLD = 600;    // Ngưỡng ánh sáng để bật đèn LED khi trời tối

DHT dht(DHTPIN, DHTTYPE);

WiFiServer server(80); // Khởi tạo server lắng nghe ở port 80

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  pinMode(LED_PIN, OUTPUT);
  pinMode(LED_LIGHT_PIN, OUTPUT);
  pinMode(LED_NHAC, OUTPUT);
  digitalWrite(LED_PIN, LOW);        // Khởi đầu tắt LED nhiệt độ/độ ẩm
  digitalWrite(LED_LIGHT_PIN, LOW);  // Khởi đầu tắt LED ánh sáng
  digitalWrite(LED_NHAC, LOW);

  // Kết nối WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Đang kết nối đến WiFi...");
  }
  Serial.println("Đã kết nối WiFi");
  Serial.println(WiFi.localIP());

  // Khởi động server
  server.begin();
}

void loop() {
  
  checkFacialRecognition();



  // Đọc giá trị cảm biến và điều khiển LED như cũ
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int lightLevel = analogRead(LDR_PIN);

  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Không đọc được nhiệt độ hoặc độ ẩm từ DHT11");
    return;
  }

  // Kiểm tra nhiệt độ và độ ẩm để bật LED
  if (temperature > TEMP_THRESHOLD) {
    digitalWrite(LED_PIN, HIGH);  

  } else if (humidity > HUM_THRESHOLD) { 
    digitalWrite(LED_PIN, HIGH);  

  } else {
    digitalWrite(LED_PIN, LOW);   
  }

  // Kiểm tra ánh sáng để bật LED khi trời tối
  if (lightLevel > LIGHT_THRESHOLD) {
    digitalWrite(LED_LIGHT_PIN, HIGH);  

  } else {
    digitalWrite(LED_LIGHT_PIN, LOW);   
  }

  delay(2000); // Đọc giá trị mỗi 2 giây
}
void checkFacialRecognition() {
    WiFiClient client = server.available(); // Kiểm tra kết nối từ client
    if (client) { // Nếu có client kết nối
        Serial.println("Nhận khuôn mặt thành công");

        String command = client.readStringUntil('\n'); // Đọc lệnh từ client
        command.trim();  // Loại bỏ khoảng trắng thừa
        Serial.println("Lệnh nhận được từ client: " + command);

        // Kiểm tra lệnh và xử lý tương ứng
        if (command == "open") {
            Serial.println("haha xin chao ");
            digitalWrite(LED_NHAC, HIGH);
            delay(20000); // bat den 20s
            digitalWrite(LED_NHAC, LOW); 
            // client.println("Open command received!");  // Gửi phản hồi đến client
        } 

        // Khi client ngắt kết nối
        client.stop();
        Serial.println("Client disconnected");
    }
}


