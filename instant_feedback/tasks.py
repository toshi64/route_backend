from .models import StudentAnswerUnit
from .components.generate_meta_userprompt import generate_meta_userprompt
from .components.define_meta_systemprompt import define_meta_systemprompt
from .components.meta_call_chatgpt_api import meta_call_chatgpt_api
from .components.save_meta_analysis import save_meta_analysis
from .components.get_context_data import get_context_data

import logging
logger = logging.getLogger(__name__)

def run_meta_analysis(answer_id):
    try:
        answer =StudentAnswerUnit.objects.get(id=answer_id)
        user = answer.session.user
        session_id = answer.session.session_id

        # プロンプト再構成
        data = {
            "session_id": session_id,
            "question_text": answer.question_text,
            "user_answer": answer.user_answer,
            "ai_feedback": answer.ai_feedback,
        }

        data = generate_meta_userprompt(data)
        past_context = get_context_data(session_id=session_id, user=user)
        meta_systemprompt = define_meta_systemprompt(past_context)

        # GPT呼び出し（メタ分析）
        data = meta_call_chatgpt_api(data, meta_systemprompt)

        # 保存
        save_meta_analysis(answer, data.get("meta_ai_feedback", ""))

        logger.info(f"[非同期] メタ分析完了 → AnswerID: {answer.id}")

    except Exception as e:
        logger.error(f"[非同期] メタ分析でエラー発生: {e}")
