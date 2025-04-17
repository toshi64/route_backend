import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

def translate_summary(material_dict: dict) -> dict:
    """
    英語の要約（summary）を日本語に翻訳し、material_dict に summary_ja を追加する関数。
    """
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    summary = material_dict.get("summary", "")
    if not summary:
        print("summary が material_dict に存在しません。")
        return material_dict

    prompt = (
        "以下の英文を中高生向けに自然で簡潔な日本語に翻訳してください。\n\n"
        + summary
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=500
        )

        translated = response.choices[0].message.content.strip()
        material_dict["summary_ja"] = translated
        print("要約の日本語訳：", translated)
        return material_dict

    except OpenAIError as e:
        print("要約の翻訳中にエラーが発生しました:", str(e))
        return material_dict
