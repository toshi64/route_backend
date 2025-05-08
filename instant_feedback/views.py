import logging
import threading
import random
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


from django.utils import timezone
from django.shortcuts import get_object_or_404
from .models import Session, EijakushindanQuestion, StudentAnswerUnit

from .tasks import run_meta_analysis

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_survey_response(request):
    user = request.user
    data = request.data

    result = save_survey_response(data, user)

    if result['status'] == 'error':
        return Response({'error': result['message']}, status=400)

    return Response({
        'message': result['message'],
        'survey_id': result['survey_id']
    }, status=201)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request):
    print("DATA RECEIVED:", request.data)
    user = request.user

    if not user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=403)

    data = request.data

    # 必須フィールドチェック
    required_fields = ['session_id', 'question_text', 'user_answer']
    for field in required_fields:
        if field not in data:
            return Response({'error': f'Missing field: {field}'}, status=400)
        

    # ユーザープロンプトを生
    data = generate_user_prompt(data)

    past_context = get_context_data(session_id=data["session_id"], user=user)
    # システムプロンプトを定義
    system_prompt = define_system_prompt(past_context)
    # ChatGPT APIを呼び出してフィードバックを生成
    data = call_chatgpt_api(data, system_prompt)

    # データベースに保存
    save_status, answer_unit = save_answer_unit(data, user)

    if answer_unit:
        threading.Thread(target=run_meta_analysis, args=(answer_unit.id,)).start()
    else:
        logger.warning("answer_unit is None — メタ分析は実行されませんでした")

        # レスポンス
    return Response({
    'ai_feedback': data.get('ai_feedback', None),
    'save_status': save_status,
    'message': 'Successfully processed and saved your answer!',
})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def session_start(request):
    user = request.user

    if not user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=403)
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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def session_end(request):
    user = request.user
    data = request.data
    session_id = data.get('session_id')

    if not session_id:
        return Response({'error': 'session_id is required.'}, status=400)

    try:
        # セッションを取得（ユーザー本人のものに限定）
        session = Session.objects.get(session_id=session_id, user=user)
    except Session.DoesNotExist:
        return Response({'error': 'Session not found.'}, status=404)

    # completed_atに現在時刻をセット
    session.completed_at = timezone.now()
    session.save()

    return Response({'message': 'Session ended successfully.'}, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def show_analysis(request):
    user = request.user
    session_id = request.query_params.get('session_id')

    if not session_id:
        return Response({'error': 'session_id is required'}, status=400)

    context_data = get_context_data(session_id=session_id, user=user)

    # メタ分析を辞書化（answer_unit.id -> meta_text）
    meta_map = {
        meta.answer.id: meta.meta_text
        for meta in context_data.get("meta_analyses", [])
    }

    # 回答とメタ分析を1つずつ統合
    results = [
        {
            "question_text": unit.question_text,
            "user_answer": unit.user_answer,
            "ai_feedback": unit.ai_feedback,
            "meta_text": meta_map.get(unit.id, "")
        }
        for unit in context_data.get("answer_units", [])
    ]

    return Response({"results": results}, status=200)



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
    all_ids = list(EijakushindanQuestion.objects.values_list('question_id', flat=True))
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
            "submit_endpoint": "/api/instant_feedback/submit/"
        }
    }

    # [Response(...) を返す]
    return Response(response_data)