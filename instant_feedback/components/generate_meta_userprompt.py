def generate_meta_userprompt(answer_dict: dict) -> dict:
    """
    メタ分析用のユーザープロンプトを、既存のdictに追加する関数。
    - 入力: question_text, user_answer, ai_feedback を含むdict
    - 出力: 同じdictに meta_user_prompt を追加して返す
    """

    question = answer_dict.get("question_text", "")
    student_answer = answer_dict.get("user_answer", "")
    ai_feedback = answer_dict.get("ai_feedback", "")

    meta_prompt = (
        f"【問題文】\n{question}\n\n"
        f"【生徒の回答】\n{student_answer}\n\n"
        f"【AIの添削フィードバック】\n{ai_feedback}\n\n"
        "これらを元に、添削の背景にある思考プロセスを分析してください。"
    )

    answer_dict["meta_userprompt"] = meta_prompt
    return answer_dict
