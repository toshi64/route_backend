import os
import openai

def call_chatgpt_api(user_prompt: str, system_prompt: str) -> str:
    """
    ChatGPT APIを呼び出し、ユーザープロンプトとシステムプロンプトを基に
    英文を生成する関数。
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # または "gpt-4"
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response['choices'][0]['message']['content']
    except openai.error.OpenAIError as e:
        print(f"ChatGPT API呼び出し中にエラーが発生しまし: {e}")
        return None
