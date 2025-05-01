
def generate_user_prompt(answer_dict: dict) -> dict:
    """
    共通のdictにuser_promptを追加する関数（英作文添削用）。
    - 入力: 'question_text', 'user_answer'を含むdict
    - 出力: 同じdictに'user_prompt'キーを追加して返す
    """

    
    question_text = answer_dict.get("question_text", "")
    user_answer = answer_dict.get("user_answer", "")

    # 生徒への出題とその回答をまとめたユーザープロンプト
    prompt_body = (
        "【出題された日本語文】\n"
        f"{question_text}\n\n"
        "【生徒の英作文】\n"
        f"{user_answer}\n\n"
        "この生徒の英作文を添削してください。"
    )

    answer_dict["user_prompt"] = prompt_body
    return answer_dict
