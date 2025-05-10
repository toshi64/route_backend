import requests
from django.conf import settings

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
