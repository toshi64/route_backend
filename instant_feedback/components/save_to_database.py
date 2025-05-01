from ..models import Session, StudentAnswerUnit, MetaAnalysis

def save_answer_unit(data: dict, user) -> tuple[str, StudentAnswerUnit | None]:
    """
    保存ステータスと、保存されたインスタンス（成功時）を返す。
    """
    try:
        session = Session.objects.get(session_id=data['session_id'], user=user)

        answer_unit = StudentAnswerUnit.objects.create(
            session=session,
            question_text=data['question_text'],
            user_answer=data['user_answer'],
            ai_feedback=data['ai_feedback']
        )

        return "保存成功", answer_unit

    except Session.DoesNotExist:
        return "保存失敗: セッションが存在しません", None

    except Exception as e:
        return f"保存失敗: {str(e)}", None


def save_meta_analysis(answer_unit: StudentAnswerUnit, meta_text: str) -> str:
    """
    MetaAnalysis を保存する関数。
    - 成功時: "保存成功"
    - 失敗時: エラーメッセージ
    """
    try:
        MetaAnalysis.objects.create(
            answer=answer_unit,
            meta_text=meta_text
        )
        return "保存成功"

    except Exception as e:
        return f"保存失敗: {str(e)}"
