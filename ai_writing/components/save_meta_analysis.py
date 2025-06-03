from instant_feedback.models import (
    StudentAnswerUnit,
)

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
