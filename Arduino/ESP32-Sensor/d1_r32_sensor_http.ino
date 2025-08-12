//esp32-F359E8
#include <WiFi.h>
#include <esp_now.h>

const int sensorPin1 = 14;  // IR 센서 1 핀
const int sensorPin2 = 16;  // IR 센서 2 핀

// ESP32-CAM의 MAC 주소 (수신기)
uint8_t receiverMac[] = {0xa0, 0xa3, 0xb3, 0x30, 0x89, 0x9c}; 
typedef struct struct_message {
  int sensor1;
  int sensor2;
} struct_message;

struct_message sensorData;

// ESP-NOW 전송 콜백
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("Last Packet Send Status: ");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Success" : "Fail");
}

void setup() {
  Serial.begin(115200);
  pinMode(sensorPin1, INPUT);
  pinMode(sensorPin2, INPUT);

  WiFi.mode(WIFI_STA); // ESP-NOW는 STA 모드로 설정해야 함
  Serial.println("ESP-NOW Sender");

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  esp_now_register_send_cb(OnDataSent);

  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, receiverMac, 6);
  peerInfo.channel = 0;  
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK){
    Serial.println("Failed to add peer");
    return;
  }
}

void loop() {
  sensorData.sensor1 = digitalRead(sensorPin1);
  sensorData.sensor2 = digitalRead(sensorPin2);

  esp_err_t result = esp_now_send(receiverMac, (uint8_t *) &sensorData, sizeof(sensorData));

  if (result == ESP_OK) {
    Serial.println("Sent sensor data via ESP-NOW");
  } else {
    Serial.println("Error sending the data");
  }

  delay(1000); // 1초마다 전송
}
