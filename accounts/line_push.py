import requests
from django.conf import settings

def push_message_to_user(line_user_id, message_text):
    url = 'https://api.line.me/v2/bot/message/push'
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}',
    }
    data = {
        'to': line_user_id,
        'messages': [
            {
                'type': 'text',
                'text': message_text,
            }
        ]
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code != 200:
        raise Exception(f"Push失敗: {response.status_code}, {response.text}")
    return response.json()
