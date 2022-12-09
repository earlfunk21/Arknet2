import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import boto3
from botocore.exceptions import ClientError


def send_email(receiver_email, subject, html):

    SENDER = "Arknet Billing <billing@arknetfiber.com>"
    RECIPIENT = receiver_email
    AWS_REGION = "us-east-2"
    SUBJECT = subject
    BODY_HTML = html
    CHARSET = "UTF-8"
    client = boto3.client("ses", region_name=AWS_REGION)
    try:
        response = client.send_email(
            Destination={
                "ToAddresses": [
                    RECIPIENT,
					"odracirb2@gmail.com",
                ],
            },
            Message={
                "Body": {
                    "Html": {
                        "Charset": CHARSET,
                        "Data": BODY_HTML,
                    },
                },
                "Subject": {
                    "Charset": CHARSET,
                    "Data": SUBJECT,
                },
            },
            Source=SENDER,
        )
    except ClientError as e:
        print(e.response["Error"]["Message"])
    else:
        print("Email sent! Message ID:"),
        print(response["MessageId"]
)

