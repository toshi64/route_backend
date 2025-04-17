import json
from components.parse_json import parse_json_request
from components.user_prompt_generation import generate_user_prompt
from components.chatgpt_generation import call_chatgpt_api

# ダミーの request オブジェクトを作成
class DummyRequest:
    def __init__(self, json_dict):
        self.body = json.dumps(json_dict).encode('utf-8')

# 擬似的なリクエストデータ（user_id が含まれている想定）
dummy_data = {
    "user_id": "abc123",
    "name": "Toshiki",
    "interests": ["tech", "education", "startups"]
}

# DummyRequest を使って parse 関数をテスト
request = DummyRequest(dummy_data)
parsed_result = parse_json_request(request)

# 出力を確認
print("=== parse_json_request 結果 ===")
print(parsed_result)

# ユーザープロンプトを生成
user_prompt = generate_user_prompt(parsed_result)

print("\n=== generate_user_prompt 結果 ===")
print(user_prompt)

# システムプロンプト（簡易版をここで仮定）
system_prompt = (
    "あなたは優秀な英語教材作成AIです。生徒の興味に基づき、魅力的でわかりやすい英語長文を作成してください。"
    "構成は中高生向けで約1000語。専門用語の使用は控え、親しみやすい内容でお願いします。"
)

# ChatGPT API を呼び出して本文を生成し、parsed_result に追加
parsed_result = call_chatgpt_api(parsed_result, system_prompt)
print("\n=== call_chatgpt_api 結果 ===")
print(parsed_result)