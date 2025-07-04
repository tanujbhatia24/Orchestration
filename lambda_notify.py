import json
import os
import urllib3
import time
import boto3

http = urllib3.PoolManager()

def send_email(subject, body):
    ses = boto3.client('ses', region_name='ap-south-1')

    response = ses.send_email(
        Source=os.environ['SES_FROM'],
        Destination={'ToAddresses': [os.environ['SES_TO']]},
        Message={
            'Subject': {'Data': subject},
            'Body': {'Text': {'Data': body}}
        }
    )
    print("SES email sent:", response['MessageId'])

def lambda_handler(event, context):
    print("SNS event received:", json.dumps(event))

    token = os.environ['TELEGRAM_TOKEN']
    chat_id = os.environ['TELEGRAM_CHAT_ID']

    for record in event['Records']:
        sns_msg = record['Sns']['Message']
        subject = record['Sns'].get('Subject', 'Deployment Notification')

        # Format message
        formatted_msg = f"*{subject}*\n\n{sns_msg}\n\n🕒 `{time.strftime('%Y-%m-%d %H:%M:%S')}`"

        # Send to Telegram
        payload = {
            "chat_id": chat_id,
            "text": formatted_msg,
            "parse_mode": "Markdown"
        }

        try:
            response = http.request(
                "POST",
                f"https://api.telegram.org/bot{token}/sendMessage",
                body=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            print("Telegram response:", response.status)
        except Exception as e:
            print("Telegram error:", str(e))

        # Send Email
        try:
            send_email(subject, sns_msg)
        except Exception as e:
            print("SES email error:", str(e))
