import dash
from dash import Dash, html, dcc, Input, Output, callback
import dash_daq as daq
import Freenove_DHT as DHT
import pytz
import dash_bootstrap_components as dbc
from paho.mqtt import client as mqtt_client
from dash import html, dcc, Output, Input
from dash.dependencies import Input, Output
#from bluepy.btle import Scanner
import bluetooth
import sqlite3

#import smtplib
#import email
#import imaplib

from datetime import datetime
import RPi.GPIO as GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
import time
#from email import policy
#from email.parser import BytesParser
#from email.header import decode_header
from Emails import read_emails, send_email
conn = sqlite3.connect('phase4.db')
c = conn.cursor()



#FAN_PIN = 17

#GPIO.setup(FAN_PIN, GPIO.OUT)

Motor1 = 22 # Enable Pin
Motor2 = 27 # Input Pin
Motor3 = 4 # Input Pin
global ledPin
ledPin = 21
GPIO.setup(ledPin, GPIO.OUT)

GPIO.setup(Motor1,GPIO.OUT, initial=GPIO.LOW)
GPIO.setup(Motor2,GPIO.OUT, initial=GPIO.HIGH)
GPIO.setup(Motor3,GPIO.OUT, initial=GPIO.LOW)

fan_status = False

global current_light_intensity
currentLightIntensity = "NaN"
global lightIntensity
global cursor
global emailadd
emailadd = 'robertojc2003@gmail.com'
global tempthresh
tempthresh = 50
global lightthresh
lightthresh = 500
global usertag
usertag = ""
global username
username = ""
global humiditynum
humiditynum = ""
global lightsrc
lightsrc = ""

broker = '172.20.10.2'
# broker = '192.168.42.159'
port = 1883
global topic 
global topic2
topic = "IoTPhase3/LightIntensity"
topic2 = "IoTPhase4/RFIDTag"
emailSent = False

app = dash.Dash(__name__)


# app.layout (before the HTML components)

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css', '/assets/styles.css']

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])


# Define the URLs for the fan images
#fan_on_image_url = "https://thumbs.dreamstime.com/b/fan-switch-button-line-icon-linear-style-sign-mobile-concept-web-design-ventilation-system-control-outline-vector-icon-166255346.jpg"
fan_on_image_url = 'Images/fanon.gif'
fan_off_image_url = 'Images/fanoff.gif'


DHT_PIN = 17
#GPIO.setup(DHT_PIN, GPIO.IN)
# Change this to the appropriate GPIO pin number
#GPIO.setup(FAN_PIN, GPIO.OUT)
# Function to read temperature from DHT11 sensor
dht = DHT.DHT(DHT_PIN)

def read_humidity():
    dht.readDHT11()
    #print(dht.humidity)
    return dht.humidity

def read_temperature():
    for i in range(0,15):
        chk = dht.readDHT11() #read DHT11 and get a return value. Then determine whether
        if (chk is dht.DHTLIB_OK): #read DHT11 and get a return value. Then determine
           
            print("DHT11,OK!")
            break
        time.sleep(0.1) 
    dht.readDHT11()
#     print(dht.temperature)
    return  dht.temperature
#layout
app.layout = html.Div([
    html.H1("Dashboard", style={'textAlign': 'center'}),
    dcc.Interval(
        id='interval-component',
        interval=15000,  # Update every 5 seconds
        n_intervals=0
    ),
    html.Hr(),
    dbc.Container(children=[
        dbc.Row([
            dbc.Col(
                html.Div(children=[
                    html.Div(style={'textAlign': 'center'}, children=[
                        html.H2('RFID Tag', style={'fontSize': '24px'}),
                        dcc.Input(id='user-tag', type='text', placeholder='', disabled=True, value=""),
                    ]),

                    html.Div(style={'textAlign': 'center'}, children=[
                        html.H2('Name', style={'fontSize': '24px'}),
                        dcc.Input(id='input-name', type='text', placeholder='', disabled=True, value=""),
                    ]),

                    html.Div(style={'textAlign': 'center'}, children=[
                        html.H2('TempThreshold', style={'fontSize': '24px'}),
                        dcc.Input(id='input-temp', type='text', placeholder='', disabled=True, value=""),
                    ]),

                    html.Div(style={'textAlign': 'center'}, children=[
                        html.H2('HumidityThreshold', style={'fontSize': '24px'}),
                        dcc.Input(id='input-humid', type='text', placeholder='', disabled=True, value=""),
                    ]),

                    html.Div(style={'textAlign': 'center'}, children=[
                        html.H2('LightThreshold', style={'fontSize': '24px'}),
                        dcc.Input(id='input-light', type='text', placeholder='', disabled=True, value=""),
                    ]),
                    html.Div(style={'textAlign': 'center'}, children=[
                        html.H2('Email', style={'fontSize': '24px'}),
                        dcc.Input(id='input-email', type='text', placeholder='', disabled=True, value=""),
                    ]),
                    html.P(''),
                    html.Button('Submit', id='submit-button2', n_clicks=0),
                    html.P(id='submit-message2', style={'textAlign': 'center'})

                ], style={'textAlign': 'center', 'border': '5px solid #00008B'}),
            ),
            dbc.Col(
                
                    [
                    html.Div([
                        html.H2("Temperature", style={'textAlign': 'center'}),
                        daq.Gauge(
                            id='temperature-gauge',
                            color="#9B51E0",
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
                            color="#9B51E0",
                            showCurrentValue=True,
                            value=0,
                            min=0,
                            max=100
                        )
                    ], className="six columns", style={'margin': '10px',
                            
                            'padding': '10px', 
                            'textAlign': 'center'
                    }),
                
            ], style={'textAlign': 'center', 'borderLeft': '5px solid #00008B', 'borderTop': '5px solid #00008B',
                      'borderBottom': '5px solid #00008B'}),
            dbc.Col([
                html.Div([
                    html.H2("Light Intensity", style={'textAlign': 'center'}),
#                     daq.Gauge(
#                         id='lightIntensity-gauge',
#                         color={"gradient": True,
#                                "ranges": {"green": [0, 24], "yellow": [24, 26], "red": [26, 50]}},
#                         showCurrentValue=True,
#                         value=0,
#                         min=0,
#                         max=1200
#                     )
                    html.Img(id='lightImage', src="/assets/Images/bulboff.png", width=200, style={'display': 'block', 'margin': 'auto'}),
                    daq.Slider(
                        id='lightIntensity-gauge',
                        min=0,
                        max=1200,
                        value=0,
                        handleLabel={"showCurrentValue": True,"label": "VALUE"},
                        step=10
                    )
                ], className="six columns", style={'margin': '10px', 'padding': '10px', 'textAlign': 'center'}),

                html.Div([
                    html.H2("Fan Status", style={'textAlign': 'center'}),
                    html.Img(id='fan-image', src="/assets/Images/fanoff.gif", width=200, style={'display': 'block', 'margin': 'auto'}),

                ], className="six columns", style={'margin': '10px', 'padding': '10px', 'textAlign': 'center'
                                                   }),
            
            ], style={'textAlign': 'center', 'borderRight': '5px solid #00008B', 'borderTop': '5px solid #00008B',
                      'borderBottom': '5px solid #00008B'}),
            # dbc.Col(children=[
            #     html.Div([
            #         html.H1('Bluetooth Devices '),
            #         dcc.Interval(
            #             id='bluetooth-interval-component',
            #             interval=1000,  # Update every 5 seconds
            #             n_intervals=0
            #         ),
            #         html.Div(id='bluetooth-devices-list'),
            #     ])
            # ], style={'border':'5px solid #00008B'})
        ])
    ]),
])


# @app.callback(
#     Output('submit-message2', 'children'),
#     Input('submit-button2', 'n_clicks'),
    
# )
# def insert_values_into_database(n_clicks, tag_id, temp, humid, light):
#     if n_clicks > 0:
#         # Connect to the database
#         conn = sqlite3.connect('phase4.db')
#         c = conn.cursor()

#         # Insert the values into the database
#         c.execute("UPDATE users SET TempThreshold = ?, HumidityThreshold = ?, LightThreshold = ? WHERE tag_id = ?", (temp, humid, light, tag_id))

#         conn.commit()

#         # Close the database connection
#         conn.close()

#         # Return a success message
#         return "Values successfully inserted into the database."

                      
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
    #fan_status = GPIO.input(Motor1)
#     if fan_status:
#         fan_image_src = fan_on_image_url
#     else:
#         fan_image_src = fan_off_image_url
    print(current_temperature)
    print(current_humidity)
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
    global canSend, fan_off_image_url, fan_on_image_url
    global fanOn
    global tempthresh
    temperature = read_temperature()

    
    if (fanOn and temperature < tempthresh):
        canSend = True
        fanOn = False
        fan_image_src = app.get_asset_url(fan_off_image_url)
        enable_fan(False)
      
        return fan_image_src  

    if (temperature > tempthresh and canSend):
        message = f"The current temperature is {temperature}. Would you like to turn on the fan?"
        send_email("Temperature is High", message, emailadd)
        canSend = False
        print("Email Sent")

    #user_response = check_email_for_user_response()
        wait = True
        while wait :
            emailReceivedContent = read_emails(emailadd)
            print(emailReceivedContent)
            if emailReceivedContent is not None:
                if emailReceivedContent == "yes":
                    wait = False
                    fanOn = True
                    fan_image_src = app.get_asset_url(fan_on_image_url)
                    print("fan is on")
                    enable_fan(True)
                  
                    return fan_image_src
                else:
                    fan_image_src = app.get_asset_url(fan_off_image_url)
                    fanOn = False
                 
                    return fan_image_src
            time.sleep(2)
    if (fanOn and temperature > tempthresh):
        fan_image_src = app.get_asset_url(fan_on_image_url)
     
        return fan_image_src
    
    fan_image_src = app.get_asset_url(fan_off_image_url)
    print(fan_off_image_url)
    return fan_image_src  
  

#     if user_response == "fanOn":
#         return temperature, fan_image_src
#     return no_update, temperature, temperature, humidity, humidity

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client()
    client.on_connect = on_connect
    client.connect(broker, port)
    return client

# @app.callback(
#     Output('bluetooth-devices-list', 'children'),
#     Input('bluetooth-interval-component', 'n_intervals'),
#     prevent_initial_call=True
# )
# def scan_bluetooth_devices(n_intervals):
#     try:
#         devices = bluetooth.discover_devices()
#         bluetooth_device_count = len(devices)
#         return bluetooth_device_count
#     except Exception as e:
#         #print("Error discovering devices: {e}")
#         return "No devices detected"

def subscribe(client: mqtt_client):
    global topic
    global topic2
    def on_message(client, userdata, msg):
        global lightthresh, ledPin, canSend
        global tempthresh
        global emailadd
        global usertag
        global username
        global humiditynum
        global lightsrc
        if (msg.topic == "IoTPhase3/LightIntensity"):
            global emailSent
            #print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
            lightmsg = ""
            lightIntensity = 0
            lightmsg = int(msg.payload.decode())
            currentLightIntensity = lightmsg
            if(int(msg.payload.decode()) <= lightthresh):
                GPIO.output(ledPin, GPIO.HIGH)
                lightsrc = "/assets/Images/lightimage.png"
                
                #uncomment for the email sent, with mine there are some issues but it seems to be the correct format (don't want to spam)
                if (emailSent == False):
                    time = datetime.now(pytz.timezone('America/New_York'))
                    currtime = time.strftime("%H:%M")
                    send_email("Light", "The Light is ON at " + currtime + ".", emailadd)
                    emailSent = True
                
            else:
                GPIO.output(ledPin, GPIO.LOW)
                lightsrc = "/assets/Images/bulboff.png"
                emailSent = False
                
                
            global current_light_intensity
            current_light_intensity = float(msg.payload.decode())
            
            
            
        elif msg.topic == "IoTPhase4/RFIDTag":
            print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

            tagnumber = msg.payload.decode()
            print(tagnumber)
            

        
            conn = sqlite3.connect('phase4.db')
            c = conn.cursor()
            
            rows = c.execute(
                "SELECT * FROM users WHERE rfid_tag = ?",
                (tagnumber,),
            ).fetchall()
            print(rows)
            emailadd = rows[0][6]
            lightthresh = rows[0][5]
            tempthresh = rows[0][3]
            usertag = rows[0][1]
            username = rows[0][2]
            humiditynum = rows[0][4]
            canSend = True
            time = datetime.now(pytz.timezone('America/New_York'))
            currtime = time.strftime("%H:%M")
            send_email("User Sign In", "New user {" + username + "} signed in at " + currtime, emailadd)
            
            
    client.subscribe(topic)
    client.subscribe(topic2)
    client.on_message = on_message
    return currentLightIntensity

@app.callback(Output('user-tag', 'value'),
              Output('input-name', 'value'),
              Output('input-temp', 'value'),
              Output('input-light', 'value'),
              Output('input-humid', 'value'),
              Output('input-email', 'value'),
              Input('interval-component', 'n_intervals'))
def updateProfile(n_intervals):
    global username
    global usertag
    global emailadd
    global lightthresh
    global tempthresh
    global humiditynum
    return usertag or "", username or "", tempthresh or "", lightthresh or "", humiditynum or "", emailadd or ""

def subscribeRFID(client: mqtt_client):
    def on_message(client, userdata, msg):
        global emailSent
        
       
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")

        tagnumber = msg.payload.decode()
        print(tagnumber)
        

    
        conn = sqlite3.connect('phase4.db')
        c = conn.cursor()
        
        rows = c.execute(
            "SELECT* FROM users WHERE rfid_tag = ?",
            (tagnumber,),
        ).fetchall()
        print(rows)
        
        
            
        
    client.subscribe(topic2)
    client.on_message = on_message
    return currentLightIntensity


@app.callback(Output('lightIntensity-gauge', 'value'),
              Output('lightImage', 'src'),
              Input('interval-component', 'n_intervals'))
def update_light_intensity(n):
    global lightsrc, current_light_intensity
    #print('elo')
    return current_light_intensity, lightsrc

def main():
    # db_file = "smarthome.db"
    # conn = create_connection(db_file)

    try:
        # db_file = "smarthome.db"
        # conn = create_connection(db_file)
       
        client = connect_mqtt()
        subscribe(client)
        #subscribeRFID(client)
        client.loop_start()

        if __name__ == '__main__':
            app.run_server(debug=True)

    finally:
        # This block will be executed on program termination
        GPIO.cleanup()
    

main()

