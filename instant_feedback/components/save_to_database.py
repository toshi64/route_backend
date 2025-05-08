from ..models import Session, StudentAnswerUnit, EijakushindanQuestion

def save_answer_unit(data: dict, user) -> tuple[str, StudentAnswerUnit | None]:
    """
    保存ステータスと、保存されたインスタンス（成功時）を返す。
    """

    try:
        session = Session.objects.get(session_id=data['session_id'], user=user)

        try:
            question = EijakushindanQuestion.objects.get(question_id=data["question_id"])
        except EijakushindanQuestion.DoesNotExist:
            return "保存失敗: 該当する問題が見つかりません", None

        answer_unit = StudentAnswerUnit.objects.create(
            session=session,
            question=question,
            question_text=data['question_text'],
            user_answer=data['user_answer'],
            ai_feedback=data['ai_feedback']
        )

        return "保存成功", answer_unit

    except Session.DoesNotExist:
        return "保存失敗: セッションが存在しません", None

    except Exception as e:
        return f"保存失敗: {str(e)}", None
