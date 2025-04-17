import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

def call_chatgpt_api(material_dict: dict, system_prompt: str) -> dict:
    """
    共通のdictを受け取り、ChatGPT APIを使ってlong_textを生成・追加する関数。
    """

    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    user_prompt = material_dict.get("user_prompt", "")
    print("=== ChatGPT API デバッグ情報 ===")
    print(f"受け取ったユーザープロンプト:\n{user_prompt}")
    print(f"受け取ったシステムプロンプト:\n{system_prompt}")
    print("ChatGPT API呼び出しを開始します...")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # または "gpt-4"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        print("ChatGPT API呼び出し成功！")
        long_text = response.choices[0].message.content
        print(f"生成された本文:\n{long_text}")

        # dictに追加して返す
        material_dict["text"] = long_text
        print(material_dict)
        return material_dict

    except OpenAIError as e:
        print("ChatGPT API呼び出し中にエラーが発生しました。")
        print(f"エラー内容: {e}")
        material_dict["long_text"] = None
        return material_dict
