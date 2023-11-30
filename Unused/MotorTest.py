import dash
import dash_daq as daq
import Freenove_DHT as DHT
from dash import html, dcc, Output, Input
from dash.dependencies import Input, Output

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

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
#FAN_PIN = 17

#GPIO.setup(FAN_PIN, GPIO.OUT)

Motor1 = 24 # Enable Pin
Motor2 = 27 # Input Pin
Motor3 = 4 # Input Pin  
GPIO.setup(Motor1,GPIO.OUT)
GPIO.setup(Motor2,GPIO.OUT)
GPIO.setup(Motor3,GPIO.OUT)
GPIO.cleanup()
fan_status = False

app = dash.Dash(__name__)


# Dash layout
import dash
import dash_daq as daq
from dash import html, dcc, Output, Input
import RPi.GPIO as GPIO

# app.layout (before the HTML components)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', '/assets/styles.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


# Define the URLs for the fan images
fan_on_image_url = "https://thumbs.dreamstime.com/b/fan-switch-button-line-icon-linear-style-sign-mobile-concept-web-design-ventilation-system-control-outline-vector-icon-166255346.jpg"
fan_off_image_url = "https://thumbs.dreamstime.com/b/air-ventilation-off-switch-button-line-icon-air-ventilation-off-switch-button-line-icon-linear-style-sign-mobile-concept-166255489.jpg"


DHT_PIN = 17
#GPIO.setup(DHT_PIN, GPIO.IN)
# Change this to the appropriate GPIO pin number
#GPIO.setup(FAN_PIN, GPIO.OUT)
# Function to read temperature from DHT11 sensor
dht = DHT.DHT(DHT_PIN)
def read_humidity():
    dht.readDHT11()
    print(dht.humidity)
    return dht.humidity

def read_temperature():
    #dht = DHT.DHT(DHT_PIN)
    #chk = dht.readDHT11()
#     if(chk is dht.DHTLIB_OK):
    #temperature = dht.temperature
#         return temperature
    dht.readDHT11()
    print(dht.temperature)
    return  dht.temperature
#layout
app.layout = html.Div([
    html.H1("Dashboard", style={'textAlign': 'center'}),
    dcc.Interval(
        id='interval-component',
        interval=5000,  # Update every 5 seconds
        n_intervals=0
    ),
    html.Div([
        html.Div([
            html.H2("Temperature", style={'textAlign': 'center'}),
            daq.Gauge(
                id='temperature-gauge',
                color={"gradient": True, "ranges": {"green": [0, 24], "yellow": [24, 26], "red": [26, 50]}},
                showCurrentValue=True,
                value=0,
                min=0,
                max=40
            )
        ], className="six columns", style={'margin': '10px', 'padding': '10px', 'textAlign': 'center'}),

        html.Div([
            html.H2("Humidity", style={'textAlign': 'center'}),
            daq.Gauge(
                id='humidity-gauge',
                color={"gradient": True, "ranges": {"green": [0, 24], "yellow": [24, 26], "red": [26, 50]}},
                showCurrentValue=True,
                value=0,
                min=0,
                max=100
            )
        ], className="six columns", style={'margin': '10px', 'padding': '10px', 'textAlign': 'center'}),

        html.Div([
            html.H2("Fan Status", style={'textAlign': 'center'}),
            html.Img(id='fan-image', width=200, style={'display': 'block', 'margin': 'auto'}),
        ], className="six columns", style={'margin': '10px', 'padding': '10px', 'textAlign': 'center'}),
    ], className="row"),
])


                      
# Callback to update temperature gauge and fan image
@app.callback(
    Output('temperature-gauge', 'value'),
    Output('humidity-gauge', 'value'),
    Input('interval-component', 'n_intervals'),
    
)

def update_temperature(n):
    # Replace this with your actual temperature reading
    current_temperature = read_temperature()
    current_humidity = read_humidity()
    # Update the temperature gauge value
    fan_status = GPIO.input(Motor1)
#     if fan_status:
#         fan_image_src = fan_on_image_url
#     else:
#         fan_image_src = fan_off_image_url
    return current_temperature, current_humidity

# if __name__ == '__main__':
#     app.run_server(debug=True)

def enable_fan(value):
    if value is True:
        GPIO.output(Motor1,GPIO.HIGH)
        GPIO.output(Motor2,GPIO.HIGH)
        GPIO.output(Motor3,GPIO.LOW)
        value = True
        # fanPicture = app.get_asset_url('fan_on.png')
    else:
        GPIO.output(Motor1,GPIO.HIGH)
        GPIO.output(Motor2,GPIO.LOW)
        GPIO.output(Motor3,GPIO.HIGH) 
        value = False
        #  fanPicture = app.get_asset_url('fan.png')
    return value

canSend = True
fanOn = False

@app.callback(
     #Output('temperature-gauge', 'value'),
     Output('fan-image', 'src'),
     Input('interval-component', 'n_intervals'),
     prevent_initial_call=True
)
def sensor_and_email_reader(n_intervals):
    global canSend
    global fanOn
    temperature = read_temperature()
    
    if (fanOn and temperature < 20):
        canSend = True
        fanOn = False
        fan_image_src = fan_off_image_url
        return fan_image_src  
    print("here")
    if (temperature > 20 and canSend):
        message = f"The current temperature is {temperature}. Would you like to turn on the fan?"
        send_email("Temperature is High", message)
        canSend = False
        print("Email Sent")

    #user_response = check_email_for_user_response()
        wait = True
        while wait :
            emailReceivedContent = read_emails()
            print(emailReceivedContent)
            if emailReceivedContent is not None:
                if emailReceivedContent == "yes":
                    wait = False
                    fanOn = True
                    fan_image_src = fan_on_image_url
                    print("fan is on")
                    enable_fan(True)
                    return fan_image_src
                else:
                    fan_image_src = fan_off_image_url
                    fanOn = False
                    return fan_image_src
    elif (fanOn and temperature > 20):
        fan_image_src = fan_on_image_url
        return fan_image_src
    else:
        fan_image_src = fan_off_image_url
        return fan_image_src  
#     if user_response == "fanOn":
#         return temperature, fan_image_src
#     return no_update, temperature, temperature, humidity, humidity

if __name__ == '__main__':
        app.run_server(debug=True)