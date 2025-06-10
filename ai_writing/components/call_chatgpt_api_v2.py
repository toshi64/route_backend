import os
import httpx
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

def call_chatgpt_api(user_prompt: str, system_prompt: str) -> str:
    """
    ユーザープロンプトとシステムプロンプトを受け取り、
    ChatGPTの応答テキスト（str）を返す。
    """
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1200,
            timeout=30
        )
        return response.choices[0].message.content

    except (OpenAIError, httpx.RequestError, httpx.TimeoutException) as e:
        print("❌ ChatGPT API 呼び出し中にエラーが発生しました。")
        print(f"エラー内容: {e}")
        return None
