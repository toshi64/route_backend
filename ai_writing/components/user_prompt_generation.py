def generate_user_prompt(answer_dict: dict) -> str:
    """
    英作文添削用のユーザープロンプトを生成して返す関数。
    - 入力: 'question_text', 'user_answer' を含む dict
    - 出力: prompt_body（str）
    """

    question_text = answer_dict.get("question_text", "")
    user_answer = answer_dict.get("user_answer", "")

    prompt_body = (
        "【出題された日本語文】\n"
        f"{question_text}\n\n"
        "【生徒の英作文】\n"
        f"{user_answer}\n\n"
        "この生徒の英作文を添削してください。"
    )

    return prompt_body
