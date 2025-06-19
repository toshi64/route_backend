from ..models import GrammarQuestion

def generate_user_prompt(answer_dict: dict, question: GrammarQuestion) -> str:
    question_text = answer_dict.get("question_text", "")
    user_answer = answer_dict.get("user_answer", "")

    model_answer = question.answer
    genre = question.genre
    subgenre = question.subgenre

    prompt_body = (
        f"この英作文問題は「{genre} / {subgenre}」に関する構文理解を問うものです。\n"
        f"以下に示す生徒の英作文が、{subgenre}の理解として適切かどうかを判断してください。\n\n"
        "【出題された日本語文】\n"
        f"{question_text}\n\n"
        "【生徒の英作文】\n"
        f"{user_answer}\n\n"
        "【模範解答】\n"
        f"{model_answer}\n\n"
    )

    return prompt_body
