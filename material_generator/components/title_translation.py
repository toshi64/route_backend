import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

def translate_title(material_dict: dict) -> dict:
    """
    ChatGPT API を使って英文タイトルを日本語に翻訳し、material_dict に追加する関数。
    """
    load_dotenv()
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    english_title = material_dict.get("title", "")
    if not english_title:
        print("title が material_dict に存在しません。")
        return material_dict

    prompt = (
        "以下の英語タイトルを、中高生にもわかりやすい日本語タイトルに翻訳してください。\n"
        "・原文タイトル：" + english_title + "\n"
        "・日本語タイトル："
    )

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=0.5,
            max_tokens=100
        )

        translated_title = response.choices[0].message.content.strip()
        material_dict["title_ja"] = translated_title
        print("翻訳されたタイトル：", translated_title)
        return material_dict

    except OpenAIError as e:
        print("タイトル翻訳中にエラーが発生しました:", str(e))
        return material_dict
