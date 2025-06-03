import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

def meta_call_chatgpt_api(data: dict, systemprompt: str) -> dict:
    """
    メタ分析用のChatGPT API呼び出し関数。
    meta_user_prompt → meta_ai_feedback に結果を保存。
    """
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    user_prompt = data.get("meta_userprompt", "")

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": systemprompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )

        meta_feedback = response.choices[0].message.content
        data["meta_ai_feedback"] = meta_feedback
        return data

    except OpenAIError as e:
        print(f"メタ分析APIエラー: {e}")
        data["meta_ai_feedback"] = None
        return data
