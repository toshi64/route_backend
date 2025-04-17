def generate_user_prompt(material_dict: dict) -> dict:
    """
    共通のdictにuser_promptを追加する関数。
    - 入力: 'id', 'data'を含むdict
    - 出力: 同じdictに'user_prompt'キーを追加して返す
    """

    prompt_intro = (
        "以下は生徒がGoogleフォームで回答した英文に対する興味のデータです。\n"
        "これを元に英文を作ってください。\n\n"
    )

    prompt_body = ""
    for key, value in material_dict["data"].items():
        prompt_body += f"{key}：{value}n"

    full_prompt = prompt_intro + prompt_body
    material_dict["user_prompt"] = full_prompt
    return material_dict
