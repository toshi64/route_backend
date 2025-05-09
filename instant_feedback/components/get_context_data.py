from ..models import Session, StudentAnswerUnit


def get_context_data(session_id: str, user) -> dict:
    """
    セッションIDとユーザーに基づいて、AIプロンプトに貼れるコンテキストを整形して返す。
    """
    try:
        session = Session.objects.get(session_id=session_id, user=user)

        answer_units = StudentAnswerUnit.objects.filter(
            session=session
        ).select_related("meta_analysis").order_by("created_at")

        context_list = []
        q_count = a_count = f_count = m_count = 0  # 各フィールドの出現数カウント用

        for unit in answer_units:
            q = unit.question_text or ""
            a = unit.user_answer or ""
            f = unit.ai_feedback or ""
             # 安全にメタ分析を取得
            meta_obj = getattr(unit, "meta_analysis", None)
            m = getattr(meta_obj, "meta_text", "") if meta_obj else ""

            if q: q_count += 1
            if a: a_count += 1
            if f: f_count += 1
            if m: m_count += 1

            context_list.append({
                "question": q,
                "answer": a,
                "ai_feedback": f,
                "meta_analysis": m
            })

        # プロンプト整形
        prompt = ""
        for i, item in enumerate(context_list, 1):
            prompt += f"Q{i}: {item['question']}\n"
            prompt += f"A{i}: {item['answer']}\n"
            prompt += f"Feedback: {item['ai_feedback']}\n"
            prompt += f"Meta: {item['meta_analysis']}\n\n"

        prompt = prompt.strip()

        # 統計情報を末尾に付ける
        summary = (
            f"\n---\n"
            f"Total Questions: {len(context_list)}\n"
            f"Questions with question_text: {q_count}\n"
            f"Questions with answer: {a_count}\n"
            f"Questions with ai_feedback: {f_count}\n"
            f"Questions with meta_analysis: {m_count}"
        )

        return {
            "formatted_prompt": prompt + summary,
            "context_list": context_list,
            "field_counts": {
                "total": len(context_list),
                "question_text": q_count,
                "answer": a_count,
                "ai_feedback": f_count,
                "meta_analysis": m_count
            }
        }

    except Session.DoesNotExist:
        return {
            "formatted_prompt": "No context available for this session.",
            "context_list": []
        }
