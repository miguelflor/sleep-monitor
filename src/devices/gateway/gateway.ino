#include <Arduino.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <BluetoothSerial.h>
#include <WiFi.h>
#include <esp_now.h>
#include <Preferences.h>
#include <PubSubClient.h>


// OLED config
#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// Objects
BluetoothSerial BT;
WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);
Preferences prefs;

// State
typedef enum { STATE_WAITING,
               STATE_CONNECTED } AppState;
AppState state = STATE_WAITING;

// Credentials loaded from NVS or received via Bluetooth
char ssid[32] = "";
char pass[64] = "";
char broker[32] = "";

// ESP-NOW data struct — must match the sender ESP32 exactly
typedef struct {
  char topic[64];
  char payload[128];
} SensorData;

SensorData incomingData;
bool newDataReady = false;


// Simple OLED helper — up to 3 lines
void oledShow(const char *line1, const char *line2 = "", const char *line3 = "") {
  display.clearDisplay();
  display.setTextColor(SSD1306_WHITE);
  display.setTextSize(2);
  display.setCursor(0, 0);
  display.println(line1);
  display.setTextSize(1);
  display.println(line2);
  display.println(line3);
  display.display();
}


// ESP-NOW callback — just copies data and sets flag, logic handled in loop()
void onDataRecv(const esp_now_recv_info_t *info, const uint8_t *data, int len) {
  if (len == sizeof(SensorData)) {
    memcpy(&incomingData, data, sizeof(SensorData));
    newDataReady = true;
  }
}


// Bluetooth — expects "ssid|password|broker_ip" terminated with newline
void handleBluetooth() {
  if (!BT.available()) return;

  String raw = BT.readStringUntil('\n');
  raw.trim();

  int sep1 = raw.indexOf('|');
  int sep2 = raw.indexOf('|', sep1 + 1);

  if (sep1 == -1 || sep2 == -1) {
    BT.println("ERROR: use format  ssid|password|broker");
    return;
  }

  raw.substring(0, sep1).toCharArray(ssid, sizeof(ssid));
  raw.substring(sep1 + 1, sep2).toCharArray(pass, sizeof(pass));
  raw.substring(sep2 + 1).toCharArray(broker, sizeof(broker));

  // Persist to NVS so credentials survive reboot
  prefs.begin("wifi", false);
  prefs.putString("ssid", ssid);
  prefs.putString("pass", pass);
  prefs.putString("broker", broker);
  prefs.end();

  BT.println("OK: saved, connecting...");
  state = STATE_CONNECTED;
}


// WAITING state — Bluetooth on, WiFi and ESP-NOW off
void enterWaiting() {
  if (mqtt.connected()) mqtt.disconnect();
  // esp_now_deinit();
  WiFi.disconnect(true);
  delay(100);

  BT.begin("ESP32-Config");  // device name visible on phone
  // oledShow("WAITING", "Bluetooth on", "ESP32-Config");
}


// CONNECTED state — WiFi + MQTT + ESP-NOW on, Bluetooth off
void enterConnected() {
  BT.end();

  // Connect WiFi
  oledShow("CONNECTING", ssid);
  WiFi.mode(WIFI_STA);
  WiFi.begin(ssid, pass);

  int tries = 0;
  while (WiFi.status() != WL_CONNECTED && tries < 20) {
    delay(500);
    tries++;
  }

  if (WiFi.status() != WL_CONNECTED) {
    oledShow("WIFI FAIL", "Check creds");
    delay(3000);
    state = STATE_WAITING;
    return;
  }

  // Connect MQTT
  mqtt.setServer(broker, 1883);
  if (!mqtt.connect("esp32-gateway")) {
    oledShow("MQTT FAIL", broker);
    delay(3000);
    state = STATE_WAITING;
    return;
  }

  // Start ESP-NOW now that WiFi channel is set
  esp_now_init();
  esp_now_register_recv_cb(onDataRecv);

  oledShow("CONNECTED", WiFi.localIP().toString().c_str(), broker);
}


void setup() {
  Serial.begin(115200);
  delay(500);

  Wire.begin(21, 22);
  Wire.setClock(100000);

  if (!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println("OLED not found");
    while (true);
  }

  display.clearDisplay();
  display.display(); 
  delay(1000);

  // Load saved credentials from NVS
  prefs.begin("wifi", true);
  prefs.getString("ssid", "").toCharArray(ssid, sizeof(ssid));
  prefs.getString("pass", "").toCharArray(pass, sizeof(pass));
  prefs.getString("broker", "").toCharArray(broker, sizeof(broker));
  prefs.end();

  // If we have credentials, go straight to connected
  if (strlen(ssid) > 0) {
    state = STATE_CONNECTED;
    enterConnected();
  } else {
    state = STATE_WAITING;
    enterWaiting();
  }
}


void loop() {
  if (state == STATE_WAITING) {
    // Listen for credentials over Bluetooth
    oledShow("Setup Wifi","Use our app","and setup the device");
    handleBluetooth();
    // Transition triggered inside handleBluetooth()
    if (state == STATE_CONNECTED) enterConnected();
  }

  if (state == STATE_CONNECTED) {
    // Keep MQTT alive
    if (!mqtt.connected()) {
      oledShow("MQTT LOST", "Reconnecting...");
      if (!mqtt.connect("esp32-gateway")) {
        delay(3000);
        return;
      }
      oledShow("CONNECTED", WiFi.localIP().toString().c_str(), broker);
    }
    mqtt.loop();

    // Forward any ESP-NOW data to MQTT broker
    if (newDataReady) {
      newDataReady = false;
      mqtt.publish(incomingData.topic, incomingData.payload);
      Serial.printf("Published [%s] %s\n", incomingData.topic, incomingData.payload);
    }
  }
}
