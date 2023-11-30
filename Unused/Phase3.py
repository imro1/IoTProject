import dash
import dash_daq as daq
import Freenove_DHT as DHT
from dash import html, dcc, Output, Input
from dash.dependencies import Input, Output

from datetime import datetime
import RPi.GPIO as GPIO
import time
import paho.mqtt.client as mqtt

from Emails import read_emails, send_email

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

Connected = False #global variable for the state of the connection
  
broker_address= "192.168.71.159"
#port = 1883
MQTT_PATH = 'IoTProject/ESP/LightIntensity'

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
 
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MQTT_PATH)

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
 
client.connect(broker_address, 1883, 60)
 
# Blocking call that processes network traffic, dispatches callbacks and
# handles reconnecting.
# Other loop*() functions are available that give a threaded interface and a
# manual interface.
client.loop_forever()# more callbacks, etc



