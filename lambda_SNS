import json
import os
import urllib3
import time

http = urllib3.PoolManager()

def lambda_handler(event, context):
    print("SNS event received:", json.dumps(event))
    
    token = os.environ['TELEGRAM_TOKEN']
    chat_id = os.environ['TELEGRAM_CHAT_ID']

    for record in event['Records']:
        sns_msg = record['Sns']['Message']
        subject = record['Sns'].get('Subject', 'Deployment Notification')

        message = f"*{subject}*\n\n{sns_msg}\n\n `{time.strftime('%Y-%m-%d %H:%M:%S')}`"

        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "Markdown"
        }

        response = http.request("POST",
            f"https://api.telegram.org/bot{token}/sendMessage",
            body=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"})

        print("Telegram status:", response.status)
        print("Telegram response:", response.data)
