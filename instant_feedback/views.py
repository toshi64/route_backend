import logging
import threading
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
from .models import Session

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
    logger.info("=== システムプロンプトの内容 ===\n" + system_prompt)

    # ChatGPT APIを呼び出してフィードバックを生成
    data = call_chatgpt_api(data, system_prompt)

    # データベースに保存
    save_status, answer_unit = save_answer_unit(data, user)

    if answer_unit:
        threading.Thread(target=run_meta_analysis, args=(answer_unit.id,)).start()
    else:
        logger.warning("answer_unit is None — メタ分析は実行されませんでした")

    # data = generate_meta_userprompt(data)  # ← 同じdataに追記
    # meta_systemprompt = define_meta_systemprompt(past_context)


    # data = meta_call_chatgpt_api(data, meta_systemprompt)
        
    # if answer_unit:
    #     meta_save_status = save_meta_analysis(answer_unit, data.get("meta_ai_feedback", ""))
    #     logger.info(f"メタ分析保存ステータス: {meta_save_status}")


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

    response_data = {
        'answer_units': [
            {
                'question_text': unit.question_text,
                'user_answer': unit.user_answer,
                'ai_feedback': unit.ai_feedback,
            }
            for unit in context_data.get("answer_units", [])
        ],
        'meta_analyses': [
            {
                'meta_text': meta.meta_text,
            }
            for meta in context_data.get("meta_analyses", [])
        ]
    }

    return Response(response_data, status=200)