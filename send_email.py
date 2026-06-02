import json
import os
import smtplib # Import smtplib for the actual sending function
from email.mime.text import MIMEText # Import the email modules we'll need
from email.mime.multipart import MIMEMultipart
from sema import User, Candidate
from config import emailJson

# Email account credentials

sender_email = emailJson["address"]
password = emailJson["app-password"]

def send_email(person, message_file_name, user_password=""):
    message_path = os.path.join(os.path.dirname(__file__),
                                "static","messages","{name}.json"
                                .format(name=message_file_name))
    with open(message_path, 'r', encoding='utf-8') as f:
        messageJson = json.load(f)

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = person.email
    msg['Subject'] = messageJson["subject"]
    msg.attach(MIMEText(messageJson["body"]
                        .format(person=person,
                                password=user_password), 'plain'))

    # Set up the SMTP server and send the email
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, person.email, msg.as_string())
        print('Email sent successfully using Gmail SMTP server')
    except Exception as e:
        print(f'Failed to send email: {e}')
    finally:
        server.quit()
