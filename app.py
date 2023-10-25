import dash
import Freenove_DHT as DHT
from dash import html, dcc, Output, Input
import smtplib
import email
import imaplib

from datetime import datetime
import RPi.GPIO as GPIO
import time
from email import policy
from email.parser import BytesParser
from email.header import decode_header


FAN_PIN = 17
GPIO.setmode(GPIO.BCM)
#GPIO.setup(FAN_PIN, GPIO.OUT)
fan_status = False

app = dash.Dash(__name__)

def read_emails():
    email_user = 'iotThermalFan@outlook.com'  # Replace with your email
    email_pass = 'iotphase2'  # Replace with your email password

    # Connect to the IMAP server
    mail = imaplib.IMAP4_SSL('outlook.office365.com')
    mail.login(email_user, email_pass)

    # Select the 'inbox' mailbox
    mail.select('inbox')

    # Search for all emails in the inbox
    status, messages = mail.search(None, 'ALL')
    messages = messages[0].split()

    email_list = []

    for msg_id in messages:
        # Fetch the email
        status, msg_data = mail.fetch(msg_id, '(RFC822)')
        raw_email = msg_data[0][1]

        # Parse the email content
        msg = email.message_from_bytes(raw_email)

        # Decode email subject
        subject, encoding = decode_header(msg['Subject'])[0]
        if isinstance(subject, bytes):
            subject = subject.decode(encoding or 'utf-8')

        email_list.append(subject)

    # The provided code for reading and processing emails
    status, messages = mail.select("INBOX")
    N = 3
    messages = int(messages[0])

    for i in range(messages, messages - N, -1):
        res, msg = mail.fetch(str(i), "(RFC822)")
        for response in msg:
            if isinstance(response, tuple):
                msg = email.message_from_bytes(response[1])
                subject, encoding = decode_header(msg["Subject"])[0]
                if isinstance(subject, bytes):
                    subject = subject.decode(encoding)
                From, encoding = decode_header(msg.get("From"))[0]
                if isinstance(From, bytes):
                    From = From.decode(encoding)
                #print("Subject:", subject)
                #print("From:", From)
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        try:
                            body = part.get_payload(decode=True).decode()
                        except:
                            pass
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            #print(body)
                            return body
                        #else:
                        #    return "nothing"
                        #elif "attachment" in content_disposition:
                        #    filename = part.get_filename()
                        #    if filename:
                        #        folder_name = clean(subject)
                        #        if not os.path.isdir(folder_name):
                        #            os.mkdir(folder_name)
                        #        filepath = os.path.join(folder_name, filename)
                        #        open(filepath, "wb").write(part.get_payload(decode=True))
                else:
                    content_type = msg.get_content_type()
                    body = msg.get_payload(decode=True).decode()
                    if content_type == "text/plain":
                        #print(body)
                        return body
                    else:
                        return "NOTHING"
                    
                if content_type == "text/html":
                    #folder_name = clean(subject)
                    if not os.path.isdir(folder_name):
                        os.mkdir(folder_name)
                    filename = "index.html"
                    filepath = os.path.join(folder_name, filename)
                    open(filepath, "w").write(body)
                #print("=" * 100)

    mail.logout()
    return email_list


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

def turn_on_fan():
    global fan_status
    GPIO.output(FAN_PIN, GPIO.HIGH)
    fan_status = True

# Function to turn off the fan
def turn_off_fan():
    global fan_status
    GPIO.output(FAN_PIN, GPIO.LOW)
    fan_status = False

# Function to send an email
def send_email(message):
   
    smtp_server = 'smtp-mail.outlook.com'
    smtp_port = 587
    sender_email = 'iotThermalFan@outlook.com'
    sender_password = 'iotphase2'
    receiver_email = 'georgeathanasatos13@gmail.com'
    print(message)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        server.sendmail(sender_email, receiver_email, message)
        server.quit()
    except Exception as e:
        print(f"Email sending failed: {e}")

# Main temperature check and control loop
while True:
    # Replace this with code to read the actual temperature
    #current_temperature = read_temperature()  # Example temperature reading
    current_temperature = 25

    if current_temperature > 24:
        message = f"The current temperature is {current_temperature}. Would you like to turn on the fan?"
        send_email(message)

        # Assuming the user's reply is received through email, check the reply here
        #user_reply = input("Enter YES to turn on the fan: ")
        user_reply = ""
        wait = True
        while wait :
            user_reply = read_emails()
            time = datetime.now()
            ti = datetime.now().time()
            tf = ti.strftime("%I:%M %p")
            print(tf)
            if tf in user_reply:
                #wait = False
                break
                print(user_reply)
            else:
                print(user_reply)
                #wait = True
    
        if "yes" in user_reply.lower():
            print("Fan is on")
            turn_on_fan()
        else:
            print("Fan not on")
            turn_off_fan()

    time.sleep(300)  # Check temperature every 5 minutes (adjust as needed)


if __name__ == '__main__':
    app.run_server(debug=True)


