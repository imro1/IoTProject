import dash
import Freenove_DHT as DHT
from dash import html, dcc, Output, Input
#import smtplib
#import email
#import imaplib

from datetime import datetime
import RPi.GPIO as GPIO
import time
#from email import policy
#from email.parser import BytesParser
#from email.header import decode_header
from Emails import read_emails, send_email

#FAN_PIN = 17
#GPIO.setmode(GPIO.BCM)
#GPIO.setup(FAN_PIN, GPIO.OUT)

Motor1 = 22 # Enable Pin
Motor2 = 27 # Input Pin
Motor3 = 19 # Input Pin  
GPIO.setup(Motor1,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor2,GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(Motor3,GPIO.OUT, initial=GPIO.LOW)
fan_status = False

app = dash.Dash(__name__)


# Dash layout
app.layout = html.Div([
    
])

# Callback to handle button click and email response


DHT_PIN = 4  # Change this to the appropriate GPIO pin number
#GPIO.setup(FAN_PIN, GPIO.OUT)
# Function to read temperature from DHT11 sensor
def read_temperature():
    dht = DHT.DHT(DHT_PIN)
    chk = dht.readDHT11()
    if(chk is dht.DHTLIB_OK):
        
        temperature = dht.temperature
        return temperature
    return 0

#def turn_on_fan():
#    global fan_status
#   GPIO.output(FAN_PIN, GPIO.HIGH)
#    fan_status = True

# Function to turn off the fan
#def turn_off_fan():
#    global fan_status
#    GPIO.output(FAN_PIN, GPIO.LOW)
#    fan_status = False
def enable_fan(value):
    if value:
        GPIO.output(Motor1, GPIO.HIGH)
        value = True
        # fanPicture = app.get_asset_url('fan_on.png')
    else:
         GPIO.output(Motor1, GPIO.LOW)
         value = False
        #  fanPicture = app.get_asset_url('fan.png')
    return value

# Main temperature check and control loop
while True:
    
    #current_temperature = read_temperature()  # Example temperature reading
    current_temperature = 25

    if current_temperature > 24:
        message = f"The current temperature is {current_temperature}. Would you like to turn on the fan?"
        subject = 
        send_email("Temperature is High", message)

        # Assuming the user's reply is received through email, check the reply here
        #user_reply = input("Enter YES to turn on the fan: ")
        user_reply = ""
        wait = True
        while wait :
            emailReceivedContent = read_emails()
            if emailReceivedContent is not None:
                if emailReceivedContent == "yes":
                    enable_fan(True)
                    break
    elif current_temperature < 24:
        enable_fan(False)
    time.sleep(300)  # Check temperature every 5 minutes (adjust as needed)


if __name__ == '__main__':
    app.run_server(debug=True)


