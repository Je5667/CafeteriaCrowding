//esp32-F359E8 송신기
#include <WiFi.h>
#include <esp_now.h>
#include <esp_wifi.h>  // WiFi 채널 설정을 위해 필요

const int sensorPin1 = 14;  // IR 센서 1 핀
const int sensorPin2 = 16;  // IR 센서 2 핀

// ===== 수신기(ESP32-CAM) MAC 주소 =====
// 반드시 실제 수신기 MAC 주소로 변경해야 함
uint8_t receiverMac[] = {0xA0, 0xA3, 0xB3, 0x30, 0x89, 0x9C}; 

typedef struct struct_message {
  int sensor1;
  int sensor2;
  int sensor3;
  int sensor4;
} struct_message;

struct_message sensorData;

// ===== ESP-NOW 전송 콜백 =====
void OnDataSent(const uint8_t *mac_addr, esp_now_send_status_t status) {
  Serial.print("Last Packet Send Status: ");
  Serial.println(status == ESP_NOW_SEND_SUCCESS ? "Success" : "Fail");
}

void setup() {
  Serial.begin(115200);
  pinMode(sensorPin1, INPUT);
  pinMode(sensorPin2, INPUT);

  // 1. ESP-NOW를 위해 STA 모드 설정
  WiFi.mode(WIFI_STA);
  Serial.println("ESP-NOW Sender");

  // 2. 채널 강제 설정 (수신기와 동일하게 6번 채널)
  esp_wifi_set_channel(6, WIFI_SECOND_CHAN_NONE);
  Serial.println("WiFi Channel set to 6");

  // 3. ESP-NOW 초기화
  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }

  // 4. 전송 콜백 등록
  esp_now_register_send_cb(OnDataSent);

  // 5. 피어(수신기) 정보 등록
  esp_now_peer_info_t peerInfo = {};
  memcpy(peerInfo.peer_addr, receiverMac, 6);
  peerInfo.channel = 6;   // 수신기와 동일 채널
  peerInfo.encrypt = false;

  if (esp_now_add_peer(&peerInfo) != ESP_OK) {
    Serial.println("Failed to add peer");
    return;
  }
}

void loop() {
  sensorData.sensor1 = -1;
  sensorData.sensor2 = -1;
  sensorData.sensor3 = digitalRead(sensorPin1);
  sensorData.sensor4 = digitalRead(sensorPin2);

  // ESP-NOW 데이터 전송
  esp_err_t result = esp_now_send(receiverMac, (uint8_t *) &sensorData, sizeof(sensorData));
  if (result == ESP_OK) {
    Serial.println("Sent sensor data via ESP-NOW");
  } else {
    Serial.println("Error sending the data");
  }

  delay(1000 + random(0, 200));
}
