import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .components.user_prompt_generation import generate_user_prompt
from .components.system_prompt_definition import define_system_prompt
from .components.call_chatgpt_api import call_chatgpt_api
from .components.save_to_database import save_answer_unit
from .components.generate_session_id import generate_session_id
from .components.save_session_entry import save_session_entry

logger = logging.getLogger(__name__)

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

    # ユーザープロンプトを生成
    data = generate_user_prompt(data)

    # システムプロンプトを定義
    system_prompt = define_system_prompt()

    # ChatGPT APIを呼び出してフィードバックを生成
    data = call_chatgpt_api(data, system_prompt)

    # データベースに保存
    save_status = save_answer_unit(data, user)

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