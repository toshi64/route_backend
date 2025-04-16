def generate_user_prompt(user_data: dict) -> str:
    """
    アンケートのDict形式データから、ChatGPT向けのユーザープロンプトを生成する関数。
    """
    prompt_intro = "以下は生徒がGoogleフォームで回答した英文に対する興味のデータです。\nこれを元に英文を作ってください。\n\n"
    
    prompt_body = ""
    for key, value in user_data.items():
        prompt_body += f"{key}：{value}\n"

    full_prompt = prompt_intro + prompt_body
    return full_prompt
