import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

def call_chatgpt_api(user_prompt: str, system_prompt: str) -> str:
    """
    ChatGPT APIを呼び出し、ユーザープロンプトとシステムプロンプトを基に
    英文を生成する関数。デバッグ用にprintを追加。
    """
    load_dotenv()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    print("=== ChatGPT API デバッグ情報 ===")
    print(f"受け取ったユーザープロンプト:\n{user_prompt}")
    print(f"受け取ったシステムプロンプト:\n{system_prompt}")
    print("ChatGPT API呼び出しを開始します...")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        print("ChatGPT API呼び出し成功！")
        print(f"レスポンス全文:\n{response}")
        
        result = response.choices[0].message.content  # ← v1.0系ではこのアクセス方法
        print(f"生成されたコンテンツ:\n{result}")
        return result

    except OpenAIError as e:
        print("ChatGPT API呼び出し中にエラーが発生しました。")
        print(f"エラー内容: {e}")
        return None
