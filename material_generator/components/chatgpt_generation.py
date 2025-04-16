import os
from openai import OpenAI

def call_chatgpt_api(user_prompt: str, system_prompt: str) -> str:
    """
    ChatGPT APIを呼び出し、ユーザープロンプトとシステムプロンプトを基に
    英文を生成する関数。
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEYが設定されていません")

    client = OpenAI(api_key=api_key)

    try:
        response = client.completions.create(
            model="gpt-3.5-turbo",
            prompt=f"{system_prompt}\n\n{user_prompt}",
            max_tokens=2000
        )
        generated_text = response.choices[0].text.strip()
        print("生成されたテキスト：\n", generated_text)  # コンソールに出力
        return generated_text

    except Exception as e:
        print(f"ChatGPT API呼び出し中にエラーが発生しました: {e}")
        return None
