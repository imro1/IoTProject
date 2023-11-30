import dash
from dash import dcc, html
#from dash.dependencies import Input, Output, dcc
from dash.dcc import Graph
import plotly.graph_objs as go
import pandas as pd
from collections import deque
from threading import Lock
import time
import RPi.GPIO as GPIO
from paho.mqtt import client as mqtt_client
from Emails import read_emails, send_email
from datetime import datetime

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

ledPin = 21
GPIO.setup(ledPin, GPIO.OUT)

global current_light_intensity
currentLightIntensity = "NaN"
global lightIntensity

# Your Raspberry Pi IP address
broker = '172.20.10.2'
port = 1883
topic = "IoTPhase3/LightIntensity"

emailSent = False

app = dash.Dash(__name__)

# Layout of the web application
app.layout = html.Div(children=[
    html.H1(children='Photoresistor Dashboard with Gauge'),
    html.Div(className='grid-container', id='led-box', children=[
    dbc.Row([
            dbc.Col(html.Div(children=[
                html.H1(children='Current Light Intensity'),
                html.Img(src=app.get_asset_url('light_intensity.png'),width='30%', height='30%'),
                dbc.Input(
                    size="lg",
                    id='light-intensity-value',
                    className="mb-3",
                    value="The light intensity is " + str(currentLightIntensity), # + isItOn,
                    readonly = True,
                    style = {
                        'text-align': 'center',
                        'margin-top': '2%',
                        'margin-right': '5%',
                        'margin-left': '5%'
                    }
                )
            ]))        
        ])
    ]),
    #dcc.Graph(id='live-update-graph'),
    dcc.Interval(
        id='interval-component',
        interval=5*1000,  # in milliseconds
        n_intervals=0
    ),
])

# Data structure for storing photoresistor values
data_buffer = deque(maxlen=10)
lock = Lock()

def connect_mqtt() -> mqtt_client:
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client(101)
    client.on_connect = on_connect
    client.connect(broker, port)
    return client


def subscribe(client: mqtt_client):
    def on_message(client, userdata, msg):
        global emailSent
        print(f"Received `{msg.payload.decode()}` from `{msg.topic}` topic")
        lightmsg = ""
        lightIntensity = 0
        lightmsg = int(msg.payload.decode())
        currentLightIntensity = lightmsg
        if(int(msg.payload.decode()) <= 400):
            GPIO.output(ledPin, GPIO.HIGH)
            
            #uncomment for the email sent, with mine there are some issues but it seems to be the correct format (don't want to spam)
            if (emailSent == False):
                time = datetime.now(pytz.timezone('America/New_York'))
                currtime = time.strftime("%H:%M")
                send_email("Light", "The Light is ON at " + currtime + ".")
                emailSent = True
            
        else:
            GPIO.output(ledPin, GPIO.LOW)
            
            emailSent = False
            
            
        global current_light_intensity
        current_light_intensity = msg.payload.decode()
        
            
        
    client.subscribe(topic)
    client.on_message = on_message
    return currentLightIntensity


@app.callback(Output('light-intensity-value', 'value'),
              Input('interval-component', 'n_intervals'))
def update_light_intensity(n):
    return 'The current light intensity is:' + str(current_light_intensity)



def main():
    # db_file = "smarthome.db"
    # conn = create_connection(db_file)

    client = connect_mqtt()
    subscribe(client)
    client.loop_start()
    if __name__ == '__main__':
        app.run_server(debug=True)
    
  
main()


