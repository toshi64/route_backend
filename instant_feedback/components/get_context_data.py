from ..models import Session, StudentAnswerUnit

def get_context_data(session_id: str, user) -> dict:
    """
    セッションIDとユーザーに基づいて、過去の回答とメタ分析情報を取得。
    """
    try:
        session = Session.objects.get(session_id=session_id, user=user)

        answer_units = StudentAnswerUnit.objects.filter(
            session=session
        ).select_related("meta_analysis").order_by("created_at")

        return {
            "answer_units": answer_units,
            "meta_analyses": [au.meta_analysis for au in answer_units if hasattr(au, "meta_analysis")]
        }

    except Session.DoesNotExist:
        return {
            "answer_units": [],
            "meta_analyses": []
        }
