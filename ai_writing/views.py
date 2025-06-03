import logging
import threading
import random
import time
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .components.get_context_data import get_context_data
from .components.user_prompt_generation import generate_user_prompt
from .components.system_prompt_definition import define_system_prompt
from .components.call_chatgpt_api import call_chatgpt_api
from .components.save_to_database import save_answer_unit
from .components.generate_session_id import generate_session_id
from .components.save_session_entry import save_session_entry
from .components.save_survey_response import save_survey_response
from .components.define_meta_meta_systemprompt import define_meta_meta_systemprompt

from threading import Thread
from django.utils import timezone
from django.shortcuts import get_object_or_404

from instant_feedback.models import (
    Session,
    EijakushindanQuestion,
    StudentAnswerUnit,
    FinalAnalysis,
    SurveyResponse
)

logger = logging.getLogger(__name__)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def session_start(request):
    user = request.user

    if not user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=403)

    if user.first_ai_writing_done:
        return Response(
            {'error': 'このユーザーはすでに受講済みです'},
            status=409  # 409 Conflict を使用（意味的に適切）
        )

  # ★ セッションIDを発行する
    session_id = generate_session_id()

    # ★ ログに出す（確認用）
    logger.info(f"New session ID generated for user {user.id}: {session_id}")

    save_session_entry(user, session_id)

    # （次は、これをデータベースに保存する処理をこの下に入れる予定）

    # ★ 仮レスポンスでセッションIDを返す
    return Response({
        'analysis_session_id': session_id,
        'message': 'Session started successfully!'
    }, status=200)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def make_question(request):
    # [リクエスト: GET make_question]
    
    # [session_id を取得]
    session_id = request.query_params.get("session_id")
    question_number = int(request.query_params.get("n", 1))

    # [Session を取得]
    session = get_object_or_404(Session, session_id=session_id)

    # [get_all_ids()] + [get_used_ids()]
    all_ids = list(
        EijakushindanQuestion.objects
        .filter(question_id__lte=20)
        .values_list('question_id', flat=True)
    )

    used_ids = set(
        StudentAnswerUnit.objects
        .filter(session=session)
        .values_list("question_id", flat=True)
    )

    # [差集合 → 未出題からランダムに選ぶ]
    unused_ids = list(set(all_ids) - used_ids)

    if not unused_ids:
        return Response({"error": "No more questions available."}, status=404)

    selected_id = random.choice(unused_ids)

    # [モデルインスタンス取得]
    question = EijakushindanQuestion.objects.get(question_id=selected_id)

    # [format_question_response() で整形]
    response_data = {
        "type": "english_writing",
        "id": f"q{question.question_id}",
        "props": {
            "question_id": question.question_id,
            "question_number": question_number,
            "question_text": question.question_text,
            "model_answer": question.model_answer,
            "submit_endpoint": "/api/instant_feedback/submit/",
        }
    }

    # [Response(...) を返す]
    return Response(response_data)