#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN D8  // ESP32 pin GPIO5
#define RST_PIN D0 // ESP32 pin GPIO27

//const char* ssid = "farouk's phone";
//const char* password = "alloallo1";
//const char* mqtt_server = "192.168.42.159";

const char* ssid = "Georgie";
const char* password = "fanumtax";
const char* mqtt_server = "172.20.10.2";

String tagNumber = "";
WiFiClient vanieriot;
PubSubClient client(vanieriot);

const int photoresistorPin = A0;
int lightValue = 0;
MFRC522 rfid(SS_PIN, RST_PIN);

void setup_wifi() {
  delay(10);
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP-8266 IP address: ");
  Serial.println(WiFi.localIP());
}

void callback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messagein;

  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messagein += (char)message[i];
  }
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("vanieriot")) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 3 seconds");
      delay(3000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(photoresistorPin, INPUT);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  SPI.begin(); // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

  if (!client.loop())
    client.connect("vanieriot");

//  Read light intensity
  lightValue = analogRead(photoresistorPin);
//  Serial.println(lightValue);

  // Read RFID
  String tagNumber = "";
  
  if (rfid.PICC_IsNewCardPresent()) {
    Serial.println("HERE");// new tag is available
    if (rfid.PICC_ReadCardSerial()) { // NUID has been read
      MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
      Serial.print("RFID/NFC Tag Type: ");
      Serial.println(rfid.PICC_GetTypeName(piccType));

      // print UID in Serial Monitor in the hex format
      Serial.print("UID:");
      for (int i = 0; i < rfid.uid.size; i++) {
        Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
        tagNumber += (rfid.uid.uidByte[i] < 0x10 ? " 0" : " ") + String(rfid.uid.uidByte[i], HEX);
        Serial.print(rfid.uid.uidByte[i], HEX);
      }
      Serial.println(tagNumber);

      rfid.PICC_HaltA(); // halt PICC
      rfid.PCD_StopCrypto1(); // stop encryption on PCD

      // Publish RFID values
      client.publish("IoTPhase4/RFIDTag", String(tagNumber).c_str());
    }
  }

  // Publish light intensity value
  client.publish("IoTPhase3/LightIntensity", String(lightValue).c_str());

  delay(3000);
}
