# components/call_chatgpt_api.py

import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

def call_chatgpt_api(answer_dict: dict, system_prompt: str) -> dict:
    """
    共通のdictを受け取り、ChatGPT APIを使って添削テキストを生成・追加する関数。
    """

    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    user_prompt = answer_dict.get("user_prompt", "")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        feedback_text = response.choices[0].message.content

        # dictに追加して返す
        answer_dict["ai_feedback"] = feedback_text
        return answer_dict

    except OpenAIError as e:
        print("ChatGPT API呼び出し中にエラーが発生しました。")
        print(f"エラー内容: {e}")
        answer_dict["ai_feedback"] = None
        return answer_dict
