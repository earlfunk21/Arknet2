import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import boto3
from botocore.exceptions import ClientError


'''
def send_email(receiver_email, subject, html):
    sender_email = "earlfunk21@gmail.com"
    password = "qmouojxbwvnxtnhk"

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    # Create the plain-text and HTML version of your message
    text = """\
    Hi,
    How are you?
    app.arknetfiber.com"""
    

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))

    # Create secure connection with server and send email
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(
            sender_email, receiver_email, message.as_string()
        )
'''


def send_email(receiver_email, subject, html):

    SENDER = "earlfunk21@gmail.com"
    RECIPIENT = receiver_email
    CONFIGURATION_SET = "ConfigSet"
    AWS_REGION = "us-west-2"
    SUBJECT = subject
    BODY_TEXT = "Welcome to Arknet Fiber\r\n"
    BODY_HTML = html
    CHARSET = "UTF-8"
    client = boto3.client("ses", region_name=AWS_REGION)
    try:
        # Provide the contents of the email.
        response = client.send_email(
            Destination={
                "ToAddresses": [
                    RECIPIENT,
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": BODY_HTML,
                    },
                    "Text": {
                        "Charset": CHARSET,
                        "Data": BODY_TEXT,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": SUBJECT,
                },
            },
            Source=SENDER,
            # If you are not using a configuration set, comment or delete the
            # following line
            ConfigurationSetName=CONFIGURATION_SET,
        )
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"])
