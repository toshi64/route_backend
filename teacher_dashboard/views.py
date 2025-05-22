from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from instant_feedback.models import StudentAnswerUnit
from django.contrib.auth import get_user_model

User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def student_summary_view(request):
    user_id = request.data.get('user_id')

    if not user_id:
        return Response({'error': 'user_id is required'}, status=400)

    try:
        student = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response({'error': 'User not found'}, status=404)

    # StudentAnswerUnitを取得（セッション順で並び替え）
    answers = StudentAnswerUnit.objects.filter(session__user=student).order_by('-created_at')

    result = []
    for ans in answers:
        result.append({
            'session_id': ans.session.session_id,
            'question_id': ans.question.question_id if ans.question else None,
            'question_text': ans.question_text,
            'user_answer': ans.user_answer,
            'ai_feedback': ans.ai_feedback,
            'submitted_at': ans.created_at.isoformat(),
            'meta_analysis': ans.meta_analysis.meta_text if hasattr(ans, 'meta_analysis') else None
        })

    return Response({
        'user_id': student.id,
        'user_name': student.full_name,
        'answers': result,
    })
