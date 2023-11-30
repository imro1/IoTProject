import smtplib
import email
import imaplib


def send_email(subject, message, emailadd):
    smtp_server = 'smtp-mail.outlook.com'
    smtp_port = 587
    sender_email = 'iotThermalFan@outlook.com'
    sender_password = 'iotphase2'
    #receiver_email = 'georgeathanasatos13@gmail.com'
    receiver_email = emailadd

    msg = 'Subject: {}\n\n{}'.format(subject, message)

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)

        server.sendmail(sender_email, receiver_email, msg)
        server.quit()
    except Exception as e:
        print(f"Email sending failed: {e}")

def read_emails(emailadd):
    email_user = 'iotThermalFan@outlook.com'  
    email_pass = 'iotphase2'  

    mail = imaplib.IMAP4_SSL('outlook.office365.com')
    mail.login(email_user, email_pass)

    mail.select('inbox')
    #dest_address = 'georgeathanasatos13@gmail.com'
    dest_address = emailadd
    status, data = mail.search(None, 
    'UNSEEN', 
    'HEADER SUBJECT "Temperature is High"',
    'HEADER FROM "' + dest_address +  '"')

    mail_ids = []
    for block in data:
        mail_ids += block.split()
    for i in mail_ids:
        status, data = mail.fetch(i, '(RFC822)')
        for response_part in data:
            if isinstance(response_part, tuple):
                message = email.message_from_bytes(response_part[1])
                mail_from = message['from']
                mail_subject = message['subject']
                if message.is_multipart():
                    mail_content = ''
                    for part in message.get_payload():
                        if part.get_content_type() == 'text/plain':
                            mail_content += part.get_payload()
                else:
                    mail_content = message.get_payload().lower()
                
                return "yes" if "yes" in mail_content.lower() else "no"