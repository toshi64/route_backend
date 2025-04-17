import json

def parse_json_request(request):
    try:
        body = request.body.decode('utf-8')
        data = json.loads(body)

        # IDを抽出（キー名は仮に"user_id"としておきます）
        user_id = data.get("user_id")
        if not user_id:
            raise ValueError("IDが含まれていません")

        # 結果を {"id": ..., "data": ...} の形式にする
        return {
            "id": user_id,
            "data": data  # パース済みの元データ全体
        }

    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as e:
        print("JSONのパースに失敗:", str(e))
        return None
