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
from .models import GrammarQuestion, GrammarNote, AnswerUnit, AIFeedback
from django.utils.timezone import localtime
from datetime import timedelta

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
            schedule = component.schedule

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

            question_data = [{
                "id": q.id,
                "genre": q.genre,
                "subgenre": q.subgenre,
                "difficulty": q.difficulty,
                "question_text": q.question_text,
                "answer": q.answer,
            } for q in selected]

            curriculum_data = {
                "detail": component.detail  # JSONで渡す {"文型": [...], "不定詞": [...]}
            }

            greeting_structure = {
                "user_name": request.user.line_display_name or request.user.username,
                "topics": component.detail  # そのまま渡す
            }

            schedule_data = {
                "start_date": schedule.start_date.isoformat(),
                "mode": schedule.mode,
                "mode_display": schedule.get_mode_display(),  # "1週間毎日"など
            }

            return JsonResponse({
                "questions": question_data,
                "curriculum": curriculum_data,
                "greeting_structure": greeting_structure,
                "schedule": schedule_data 
            })

        except ScheduleComponent.DoesNotExist:
            return JsonResponse({"error": "Component not found"}, status=404)

    return JsonResponse({"error": "Invalid request"}, status=400)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def show_progress(request):
    component_id = request.data.get('component_id')

    try:
        component = ScheduleComponent.objects.get(component_id=component_id)
        schedule = component.schedule
        user = request.user

        # ✅ 開始日～終了日のリストを作成（daily_for_one_week対応）
        if schedule.mode == 'daily_for_one_week':
            date_list = [schedule.start_date + timedelta(days=i) for i in range(7)]
        elif schedule.mode == 'once':
            date_list = [schedule.start_date]
        else:
            return Response({"error": "未対応のスケジュールモードです"}, status=400)

        # ✅ 対象期間のAnswerUnitを取得
        answers = AnswerUnit.objects.filter(
            user=user,
            component=component,
            created_at__date__range=(date_list[0], date_list[-1])
        )

        
        today = localtime().date()

        progress_by_date = []
        for date in date_list:
            date_answers = answers.filter(created_at__date=date)

            if date_answers.exists():
                status = "done"
            elif date > today:
                status = "upcoming"
            elif date == today:
                status = "upcoming"  # ✅ 当日はまだやっていなくても upcoming にする
            else:
                status = "missed"

            progress_by_date.append({
                "date": date.isoformat(),
                "status": status,
                "answered_count": date_answers.count(),
                "session_count": date_answers.values("session").distinct().count()
            })

        print(progress_by_date)

        return Response({
            "component_id": str(component_id),
            "schedule_mode": schedule.mode,
            "start_date": schedule.start_date.isoformat(),
            "progress": progress_by_date
        })

    except ScheduleComponent.DoesNotExist:
        return Response({"error": "Component not found"}, status=404)


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

    component_id = data.get('component_id')  
    component = None
    if component_id:
        try:
            component = ScheduleComponent.objects.get(component_id=component_id)
        except ScheduleComponent.DoesNotExist:
            print(f"[警告] component_id={component_id} が見つかりませんでした。")

    # データ取得・保存処理
    try:
        session = Session.objects.get(session_id=session_id)
        question = GrammarQuestion.objects.get(id=question_id)

        answer_unit = AnswerUnit.objects.create(
            session=session,
            question=question,
            user=user,
            user_answer=user_answer,
            component=component
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_grammar_note(request):
    subgenre_name = request.query_params.get("subgenre")
    if not subgenre_name:
        return JsonResponse({"error": "subgenre parameter is required"}, status=400)

    try:
        note = GrammarNote.objects.get(subgenre=subgenre_name)
        return JsonResponse({
            "title": note.title,
            "description": note.description
        })
    except GrammarNote.DoesNotExist:
        return JsonResponse({"error": "GrammarNote not found for the given subgenre"}, status=404)