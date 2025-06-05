import logging
import random
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .components.generate_session_id import generate_session_id
from .components.save_session_entry import save_session_entry
from .components.save_session_entry import save_session_entry
from .components.user_prompt_generation import generate_user_prompt
from .components.system_prompt_definition import define_system_prompt
from .components.call_chatgpt_api import call_chatgpt_api
from .models import GrammarQuestion, AnswerUnit, AIFeedback


from django.shortcuts import get_object_or_404

from instant_feedback.models import (
    Session,
    EijakushindanQuestion,
)

from material_scheduler.models import ScheduleComponent

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

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
        AnswerUnit.objects
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




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_questions_from_component_id(request):
    if request.method == "POST":
        data = request.data
        component_id = data.get("component_id")

        try:
            component = ScheduleComponent.objects.get(component_id=component_id)
            detail = component.detail  # 例: {"文型": ["SV"], "不定詞": ["to + 動詞"]}

            questions = []
            for genre, subgenres in detail.items():
                matched = GrammarQuestion.objects.filter(
                    genre=genre,
                    subgenre__in=subgenres,
                    is_active=True
                )
                questions.extend(matched)

            questions = list({q.id: q for q in questions}.values())  # 重複排除
            selected = random.sample(questions, min(5, len(questions)))

            response = [{
                "id": q.id,
                "genre": q.genre,
                "subgenre": q.subgenre,
                "question_text": q.question_text,
                "answer": q.answer,
            } for q in selected]

            return JsonResponse(response, safe=False)

        except ScheduleComponent.DoesNotExist:
            return JsonResponse({"error": "Component not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)




@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request):
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=403)

    data = request.data

    session_id = data.get('session_id')
    question_id = data.get('question_id')
    user_answer = data.get('user_answer')

    # データ取得・保存処理
    try:
        session = Session.objects.get(session_id=session_id)
        question = GrammarQuestion.objects.get(id=question_id)

        answer_unit = AnswerUnit.objects.create(
            session=session,
            question=question,
            user=user,
            user_answer=user_answer
        )
        
        data = generate_user_prompt(data)
        system_prompt = define_system_prompt()

        data = call_chatgpt_api(data, system_prompt)

        AIFeedback.objects.create(
            answer=answer_unit,
            feedback_text=data.get('ai_feedback', '未出力')
        )
        print(data)


        return Response({
            'ai_feedback': data.get('ai_feedback', None),
            'message': 'Successfully processed and saved your answer!',
        })

    except Session.DoesNotExist:
        return Response({'error': '無効なセッションIDです'}, status=400)
    except GrammarQuestion.DoesNotExist:
        return Response({'error': '無効な問題IDです'}, status=400)
    except Exception as e:
        return Response({'error': str(e)}, status=500)
