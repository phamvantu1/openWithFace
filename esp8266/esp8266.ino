
#include <DHT.h>

#define DHTPIN D4                // Pin kết nối với DHT11
#define DHTTYPE DHT11            // Loại cảm biến DHT11
#define LED_PIN D2               // Pin LED cho nhiệt độ và độ ẩm
#define LDR_PIN A0               // Pin cho quang trở (LDR)
#define LED_LIGHT_PIN D5         // Pin LED để bật khi trời tối

const float TEMP_THRESHOLD = 33.0;  // Ngưỡng nhiệt độ để bật LED
const float HUM_THRESHOLD = 85.0;   // Ngưỡng độ ẩm để bật LED
const int LIGHT_THRESHOLD = 1000;    // Ngưỡng ánh sáng để bật đèn LED khi trời tối

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(115200);
  dht.begin();
  
  pinMode(LED_PIN, OUTPUT);
  pinMode(LED_LIGHT_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);        // Khởi đầu tắt LED nhiệt độ/độ ẩm
  digitalWrite(LED_LIGHT_PIN, LOW);  // Khởi đầu tắt LED ánh sáng
}

void loop() {
  // Đọc giá trị nhiệt độ và độ ẩm từ cảm biến DHT11
  float temperature = dht.readTemperature();
  float humidity = dht.readHumidity();
  int lightLevel = analogRead(LDR_PIN);  // Đọc giá trị ánh sáng từ quang trở

  // Kiểm tra xem có đọc được dữ liệu từ cảm biến không
  if (isnan(temperature) || isnan(humidity)) {
    Serial.println("Không đọc được nhiệt độ hoặc độ ẩm từ DHT11");
    return;
  }

  // Hiển thị giá trị nhiệt độ và độ ẩm
  Serial.print("Nhiệt độ: ");
  Serial.print(temperature);
  Serial.println("°C");
  Serial.print("Độ ẩm: ");
  Serial.print(humidity);
  Serial.println("%");

  // Kiểm tra nhiệt độ và độ ẩm để bật LED
  if (temperature > TEMP_THRESHOLD) {
    digitalWrite(LED_PIN, HIGH);  
    Serial.println("Nhiệt độ vượt ngưỡng, BẬT LED nhiệt độ/độ ẩm.");
  } else if (humidity > HUM_THRESHOLD) { 
    digitalWrite(LED_PIN, HIGH);  
    Serial.println("Độ ẩm cao, BẬT LED nhiệt độ/độ ẩm.");
  } else {
    digitalWrite(LED_PIN, LOW);   
    Serial.println("Nhiệt độ và độ ẩm dưới ngưỡng, Tắt LED nhiệt độ/độ ẩm.");
  }

  // Kiểm tra ánh sáng để bật LED khi trời tối
  Serial.print("Mức ánh sáng: ");
  Serial.println(lightLevel);
  if (lightLevel > LIGHT_THRESHOLD) {
    digitalWrite(LED_LIGHT_PIN, HIGH);  // Bật LED ánh sáng nếu trời tối
    Serial.println("Trời tối, BẬT LED ánh sáng.");
  } else {
    digitalWrite(LED_LIGHT_PIN, LOW);   // Tắt LED ánh sáng nếu đủ sáng
    Serial.println("Trời sáng, Tắt LED ánh sáng.");
  }

  delay(2000); // Đọc giá trị mỗi 2 giây
}

