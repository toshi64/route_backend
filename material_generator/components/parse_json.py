import json

def parse_json_request(request):
    try:
        body = request.body.decode('utf-8')
        data = json.loads(body)  # ← ここで dict に変換！
        return data
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print("JSONのパースに失敗:", str(e))
        return None
