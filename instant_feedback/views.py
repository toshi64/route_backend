from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .components.user_prompt_generation import generate_user_prompt
from .components.system_prompt_definition import define_system_prompt
from .components.call_chatgpt_api import call_chatgpt_api
from .components.save_to_database import save_answer_unit  # ← 追加！

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
