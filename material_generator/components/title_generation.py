import os
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError

def generate_title(material_dict: dict) -> dict:
    """
    ChatGPT APIを使って、長文に対するタイトルを生成し、material_dictに追加する関数。
    """
    load_dotenv()

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    body_text = material_dict.get("text", "")

    if not body_text:
        print("長文が存在しません。タイトル生成をスキップします。")
        return material_dict

    prompt = (
        "以下は英語学習者向けの長文です。この内容に最もふさわしい、簡潔で魅力的な英語タイトルを1行でつけてください。\n\n"
        f"{body_text}"
    )

    try:
        print("ChatGPT APIを使ってタイトル生成を開始します...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは英語教材編集のプロです。"},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=60
        )
        title = response.choices[0].message.content.strip()
        print(f"生成されたタイトル: {title}")
        material_dict["title"] = title
        return material_dict

    except OpenAIError as e:
        print("タイトル生成中にエラーが発生しました。")
        print(f"エラー内容: {e}")
        return material_dict
