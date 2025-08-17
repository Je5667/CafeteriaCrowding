#include <WiFi.h>
#include <esp_now.h>
#include "esp_camera.h"
#include <HTTPClient.h>

// ===== WiFi 접속 정보 =====
const char* ssid = "ch_iphone";
const char* password = "mmmmmmmm";

// ===== 서버 URL =====
const char* serverUrl = "http://172.20.10.3:5000/upload";

// ===== ESP32-CAM 핀 매핑 define =====
#define PWDN_GPIO_NUM     32
#define RESET_GPIO_NUM    -1
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM     26
#define SIOC_GPIO_NUM     27
#define Y9_GPIO_NUM       35
#define Y8_GPIO_NUM       34
#define Y7_GPIO_NUM       39
#define Y6_GPIO_NUM       36
#define Y5_GPIO_NUM       21
#define Y4_GPIO_NUM       19
#define Y3_GPIO_NUM       18
#define Y2_GPIO_NUM       5
#define VSYNC_GPIO_NUM    25
#define HREF_GPIO_NUM     23
#define PCLK_GPIO_NUM     22

// ===== ESP-NOW 데이터 구조체 =====
typedef struct struct_message {
  int sensor1;
  int sensor2;
  int sensor3;
  int sensor4;
} struct_message;

struct_message incomingData;

// 최신 센서값 저장 (배열 선언!)
// 0: sensor1, 1: sensor2, 2: sensor3, 3: sensor4
volatile int latest_sensor[4] = {-1, -1, -1, -1};
unsigned long sensorTimes[4] = {0, 0, 0, 0};

// BOTH 이벤트용 변수
unsigned long bothStartTime = 0;
bool bothStartArmed = false;

// 이벤트 플래그
volatile bool eventIn = false;
volatile bool eventOut = false;
volatile bool eventBoth = false;

// 판정 허용 시간(3초)
const unsigned long TIME_GAP = 3000;

// 사진 전송 함수
void captureAndSendPhoto(const char* eventType) {
  String camera_id = String(eventType) + "_doorcam01";
  Serial.printf("[사진캡처] camera_id: %s\n", camera_id.c_str());

  camera_fb_t *fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }

  if (WiFi.status() == WL_CONNECTED) {
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW");

    String bodyStart =
      "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n"
      "Content-Disposition: form-data; name=\"camera_id\"\r\n\r\n"
      + camera_id + "\r\n"
      "------WebKitFormBoundary7MA4YWxkTrZu0gW\r\n"
      "Content-Disposition: form-data; name=\"image\"; filename=\"photo.jpg\"\r\n"
      "Content-Type: image/jpeg\r\n\r\n";
    String bodyEnd = "\r\n------WebKitFormBoundary7MA4YWxkTrZu0gW--\r\n";

    int totalLen = bodyStart.length() + fb->len + bodyEnd.length();
    uint8_t *postData = (uint8_t *)malloc(totalLen);
    if (postData) {
      memcpy(postData, bodyStart.c_str(), bodyStart.length());
      memcpy(postData + bodyStart.length(), fb->buf, fb->len);
      memcpy(postData + bodyStart.length() + fb->len, bodyEnd.c_str(), bodyEnd.length());

      int httpResponseCode = http.POST(postData, totalLen);
      free(postData);

      if (httpResponseCode > 0) {
        Serial.printf("HTTP Response code: %d\n", httpResponseCode);
        Serial.println(http.getString());
      } else {
        Serial.print("Error on sending POST: ");
        Serial.println(httpResponseCode);
      }
    } else {
      Serial.println("Memory allocation failed!");
    }
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }
  esp_camera_fb_return(fb);
}

// ESP-NOW 수신 콜백
void OnDataRecv(const uint8_t * mac, const uint8_t *incomingDataPtr, int len) {
  memcpy(&incomingData, incomingDataPtr, sizeof(incomingData));
  unsigned long now = millis();

  // ----- 센서값 최신화 -----
  if (incomingData.sensor1 != -1) latest_sensor[0] = incomingData.sensor1;
  if (incomingData.sensor2 != -1) latest_sensor[1] = incomingData.sensor2;
  if (incomingData.sensor3 != -1) latest_sensor[2] = incomingData.sensor3;
  if (incomingData.sensor4 != -1) latest_sensor[3] = incomingData.sensor4;

  // ----- BOTH 감지용 -----
  // 1, 4가 동시에 ON(0)이 되는 순간만 기록 및 대기 시작
  if (latest_sensor[0] == 0 && latest_sensor[3] == 0 && !bothStartArmed) {
    bothStartTime = now;
    bothStartArmed = true;
  }

  // 1,4가 동시에 ON된 이후 3초 내에 2,3이 모두 ON(0)이 되면 BOTH 참
  if (bothStartArmed &&
      latest_sensor[1] == 0 &&
      latest_sensor[2] == 0 &&
      (now - bothStartTime <= TIME_GAP)) {
    eventBoth = true;
    bothStartArmed = false;
    eventIn = false;
    eventOut = false;
  }

  // 대기 중 3초 지나면 리셋
  if (bothStartArmed && (now - bothStartTime > TIME_GAP)) {
    bothStartArmed = false;
  }

  // --- 기본 IN/OUT 이벤트: 1->2, 4->3 판정 ---
  if (incomingData.sensor1 != -1 && incomingData.sensor1 == 0)
    sensorTimes[0] = now;
  if (incomingData.sensor4 != -1 && incomingData.sensor4 == 0)
    sensorTimes[3] = now;
  if (incomingData.sensor2 != -1 && incomingData.sensor2 == 0) {
    if (now - sensorTimes[0] <= TIME_GAP && sensorTimes[0] != 0) {
      eventIn = true;
    }
  }
  if (incomingData.sensor3 != -1 && incomingData.sensor3 == 0) {
    if (now - sensorTimes[3] <= TIME_GAP && sensorTimes[3] != 0) {
      eventOut = true;
    }
  }

  Serial.printf("1:%d 2:%d 3:%d 4:%d\n",
    latest_sensor[0], latest_sensor[1], latest_sensor[2], latest_sensor[3]);
}

void setup() {
  Serial.begin(115200);

  WiFi.mode(WIFI_AP_STA);
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");

  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sccb_sda = SIOD_GPIO_NUM;
  config.pin_sccb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;
  if (psramFound()) {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 10;
    config.fb_count = 2;
  } else {
    config.frame_size = FRAMESIZE_CIF;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x\n", err);
    return;
  }

  if (esp_now_init() != ESP_OK) {
    Serial.println("Error initializing ESP-NOW");
    return;
  }
  esp_now_register_recv_cb(OnDataRecv);
}

void loop() {
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 's') {
      captureAndSendPhoto("manual_doorcam01");
    }
  }

  if (eventBoth) {
    captureAndSendPhoto("both");
    eventBoth = false;
    eventIn = false;
    eventOut = false;
  } else if (eventIn) {
    captureAndSendPhoto("in");
    eventIn = false;
    eventOut = false;
  } else if (eventOut) {
    captureAndSendPhoto("out");
    eventOut = false;
    eventIn = false;
  }
  delay(100);
}
