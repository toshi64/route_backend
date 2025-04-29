# components/save_to_database.py

from ..models import Session, StudentAnswerUnit

def save_answer_unit(data: dict, user) -> str:
    """
    受け取ったデータ(dict)をもとにStudentAnswerUnitを保存する関数。
    保存に成功したら"保存成功"、失敗したらエラーメッセージを返す。
    """

    try:
        # セッションを取得
        session = Session.objects.get(session_id=data['session_id'], user=user)


        # StudentAnswerUnitを作成して保存
        StudentAnswerUnit.objects.create(
            session=session,
            question_text=data['question_text'],
            user_answer=data['user_answer'],
            ai_feedback=data['ai_feedback']
        )

        return "保存成功"

    except Session.DoesNotExist:
        return "保存失敗: セッションが存在しません"

    except Exception as e:
        return f"保存失敗: {str(e)}"
