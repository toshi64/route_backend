import logging
from .models import AnswerUnit, AIFeedback, MetaAnalysisResult
from .components.prompts import define_meta_analysis_system_prompt
from .components.call_chatgpt_api_v2 import call_chatgpt_api
from .components.validator import validate_meta_analysis

from instant_feedback.models import (Session)
from material_scheduler.models import ScheduleComponent
import json

logger = logging.getLogger(__name__)


def run_meta_analysis_task(session_id, component_id):
    def format_genre_detail_natural(detail: dict) -> str:
        sections = []
        for genre, subgenres in detail.items():
            if not subgenres:
                continue
            subgenre_text = "、".join(f"「{s}」" for s in subgenres)
            section = f"{genre}の{subgenre_text}"
            sections.append(section)
        body = "、".join(sections)
        return f"このセッションのテーマは、{body}についてです。"

    try:
        session = Session.objects.get(session_id=session_id)
        answers = AnswerUnit.objects.filter(session=session)
        if not answers.exists():
            print("⚠️ No answers found")
            return

        component = ScheduleComponent.objects.get(component_id=component_id)
        theme_sentence = format_genre_detail_natural(component.detail)

        answer_texts = []
        for i, answer in enumerate(answers, start=1):
            question_text = answer.question.question_text if answer.question else "（問題文なし）"
            user_input = answer.user_answer or "（未入力）"
            try:
                feedback = answer.ai_feedback.feedback_text
            except AIFeedback.DoesNotExist:
                feedback = "（未実施）"

            answer_texts.append(
                f"【第{i}問】\n"
                f"【問題文】\n{question_text}\n"
                f"【ユーザーの回答】\n{user_input}\n"
                f"【AIが行った添削】\n{feedback}\n"
                "------------------------------------"
            )

        user_prompt = (
            f"{theme_sentence}\n\n"
            f"以下の英作文の回答をもとに、生徒の理解傾向と改善点を分析してください。\n\n"
            f"{'\n'.join(answer_texts)}"
        )

        system_prompt = define_meta_analysis_system_prompt()

        MAX_RETRIES = 5
        for attempt in range(1, MAX_RETRIES + 1):
            print(f"🌀 試行 {attempt} 回目")
            ai_response = call_chatgpt_api(user_prompt, system_prompt)
            try:
                parsed = json.loads(ai_response)
                if validate_meta_analysis(parsed):
                    MetaAnalysisResult.objects.create(
                        session=session,
                        component=component,
                        score=parsed["score"],
                        advice=parsed["advice"]
                    )
                    print("✅ バリデーション成功・保存完了")
                    return
                else:
                    print("⚠️ バリデーション失敗")
            except json.JSONDecodeError:
                print("❌ JSON構文エラー")

        print("❌ 最大試行回数に達しました")

    except Session.DoesNotExist:
        print("❌ Invalid session_id")
    except ScheduleComponent.DoesNotExist:
        print(f"❌ Invalid component_id: {component_id}")
