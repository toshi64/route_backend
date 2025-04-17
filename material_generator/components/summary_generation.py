import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

def generate_summary(material_dict: dict) -> dict:
    """
    ChatGPT API を使って長文を要約し、material_dict に summary を追加する関数。
    """
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    body_text = material_dict.get("text", "")
    if not body_text:
        print("text が material_dict に存在しません。")
        return material_dict

    prompt = (
        "以下の英文を中高生向けに分かりやすく要約してください。50語程度の長さでお願いします。\n\n"
        + body_text
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=300
        )

        summary_text = response.choices[0].message.content.strip()
        material_dict["summary"] = summary_text
        print("要約結果：", summary_text)
        return material_dict

    except OpenAIError as e:
        print("要約中にエラーが発生しました:", str(e))
        return material_dict
