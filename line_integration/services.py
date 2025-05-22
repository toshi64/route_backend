import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist

User = get_user_model()

def get_line_tokens(code: str):
    url = 'https://api.line.me/oauth2/v2.1/token'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    data = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': settings.LINE_REDIRECT_URI,
        'client_id': settings.LINE_CHANNEL_ID,
        'client_secret': settings.LINE_CHANNEL_SECRET,
    }
    response = requests.post(url, headers=headers, data=data)
    if response.status_code != 200:
        raise Exception(f"LINE token取得エラー: {response.status_code}, {response.text}")
    return response.json()



def get_line_profile(access_token: str):
    url = 'https://api.line.me/v2/profile'
    headers = {'Authorization': f'Bearer {access_token}'}
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"LINEプロフィール取得エラー: {response.status_code}, {response.text}")
    return response.json()



def send_line_text_to_user(user_id: int, text: str) -> None:
    """
    指定された user_id のユーザーに対して、LINEでテキストメッセージを送信する関数（途中段階）。

    Args:
        user_id (int): DjangoのCustomUserモデルのID
        text (str): 送信したいメッセージ本文（LINEのフォーマットに準拠したもの）

    Returns:
        None
    """

    try:
        user = User.objects.get(id=user_id)
    except ObjectDoesNotExist:
        print(f"[ERROR] User with id={user_id} does not exist.")
        return

    if not user.line_user_id:
        print(f"[WARNING] User with id={user_id} has no line_user_id. Skipping LINE message.")
        return
    
    headers = {
        "Authorization": f"Bearer {settings.LINE_CHANNEL_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }

    payload = {
        "to": user.line_user_id,
        "messages": [
            {
                "type": "text",
                "text": text
            }
        ]
    }

    response = requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers=headers,
        json=payload
    )

    if response.status_code != 200:
            print(f"[ERROR] LINE API送信失敗: status={response.status_code}, body={response.text}")