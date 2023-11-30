#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <SPI.h>
#include <MFRC522.h>

// const char* ssid = "TP-Link_2AD8";
// const char* password = "14730078";
// const char* mqtt_server = "192.168.0.144";

const char* ssid = "BIG KYRG";
const char* password = "12345678";
const char* mqtt_server = "172.20.10.2";

const uint8_t SS_PIN = 15;
const uint8_t RST_PIN = 20;

// const char* ssid = "iPhone a Philip";
// const char* password = "edpo1s0kp8ty1";
// const char* mqtt_server = "172.20.10.3";

WiFiClient vanieriot;
PubSubClient client(vanieriot);
MFRC522 rfid(SS_PIN, RST_PIN); // Instance of the class
//MFRC522::MIFARE_Key key;
//byte nuidPICC[4];

const int pResistor = A0;
const int led = D0;
int value;

void setup_wifi() {
   delay(10);
   Serial.println();
   Serial.print("Connecting to ");
   Serial.println(ssid);
   WiFi.mode(WIFI_STA);
   WiFi.begin(ssid, password);
   uint32_t notConnectedCounter = 0;
   while (WiFi.status() != WL_CONNECTED) {
     delay(500);
     Serial.print(".");
     notConnectedCounter++;
      if(notConnectedCounter > 150) { // Reset board if not connected after 5s
          ESP.restart();
      }
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
     }
     else {
       Serial.print("failed, rc=");
       Serial.print(client.state());
       Serial.println(" try again in 3 seconds");
       delay(3000);
     }
   }
}
void setup() {
  Serial.begin(115200);
  pinMode(pResistor, INPUT);
  //pinMode(led,OUTPUT);
  //digitalWrite(led, LOW);
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
  // Init SPI bus
  rfid.PCD_Init(); // Init MFRC522
//  rfid.PCD_DumpVersionToSerial();
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  if(!client.loop())
    client.connect("vanieriot");

//  String tagNumber;
//  
//  if (rfid.PICC_IsNewCardPressetup_wifi();

//  client.setCallent()) { // new tag is available
//    if (rfid.PICC_ReadCardSerial()) { // NUID has been readed
//      MFRC522::PICC_Type piccType = rfid.PICC_GetType(rfid.uid.sak);
//      Serial.print("RFID/NFC Tag Type: ");
//      Serial.println(rfid.PICC_GetTypeName(piccType));
//
//      // print UID in Serial Monitor in the hex format
//      Serial.print("UID:");
//      for (int i = 0; i < rfid.uid.size; i++) {
//        Serial.print(rfid.uid.uidByte[i] < 0x10 ? " 0" : " ");
//        tagNumber += rfid.uid.uidByte[i] < 0x10 ? " 0" : " ";
//        Serial.print(rfid.uid.uidByte[i], HEX);
//        tagNumber += rfid.uid.uidByte[i], HEX;
//      }
//      Serial.println();
//
//      rfid.PICC_HaltA(); // halt PICC
//      rfid.PCD_StopCrypto1(); // stop encryption on PCD
//    }
//  }

 // client.publish("IoTPhase4/RFIDTag",String(tagNumber).c_str());
   delay(3000);
  
}
