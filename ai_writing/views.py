import logging
import random
from threading import Thread
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .components.generate_session_id import generate_session_id
from .components.save_session_entry import save_session_entry
from .components.save_session_entry import save_session_entry
from .components.user_prompt_generation import generate_user_prompt
from .components.system_prompt_definition import define_system_prompt
from .models import GrammarQuestion, GrammarNote, AnswerUnit, AIFeedback, MetaAnalysisResult
from django.utils.timezone import localtime
from datetime import timedelta
from .components.prompts import define_meta_analysis_system_prompt, define_system_prompt_for_question
from .components.call_chatgpt_api_v2 import call_chatgpt_api
from .components.validator import validate_meta_analysis
from ai_writing.tasks import run_meta_analysis_task

from django.shortcuts import get_object_or_404

from instant_feedback.models import (
    Session,
    EijakushindanQuestion,
)

from material_scheduler.models import ScheduleComponent

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import QuestionClipForGrammarSerializer
from .serializers import ReviewCandidateSerializer
from .models import QuestionClipForGrammar
from .serializers import QuestionClipDetailSerializer

logger = logging.getLogger(__name__)



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

            if component.schedule.user != request.user:
             return JsonResponse({"error": "Unauthorized"}, status=403)
            
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
    """
    DEPRECATED 2025-07-28:
    Tadoku/Stra リファクタに伴いフロントから呼ばれなくなった。
    URL ルーティングからも除外済み。将来不要なら削除。
    """
    component_id = request.data.get('component_id')

    try:
        component = ScheduleComponent.objects.get(component_id=component_id)

        if component.schedule.user != request.user:
          return JsonResponse({"error": "Unauthorized"}, status=403)
        
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
def show_session_history(request):
    user = request.user
    component_id = request.data.get("component_id")

    if not component_id:
        return Response({"error": "component_id is required"}, status=400)

    try:
        component = ScheduleComponent.objects.get(component_id=component_id)
    except ScheduleComponent.DoesNotExist:
        return Response({"error": "Invalid component_id"}, status=404)

    # 該当ユーザー & 指定コンポーネントの MetaAnalysis を取得（降順）
    results = MetaAnalysisResult.objects.filter(
        component=component,
        session__user=user
    ).order_by('-created_at')

    response_data = [
        {
            "session_id": result.session.session_id,
            "score": result.score,
            "advice": result.advice,
            "created_at": result.created_at.isoformat()
        }
        for result in results
    ]

    print(f"✅ ユーザー{user.id}のMetaAnalysis履歴（component={component_id}, 件数={len(response_data)}）")
    return Response({"session_history": response_data})


from django.db import transaction
from django.utils import timezone
import json
import logging

logger = logging.getLogger(__name__)

def call_gpt_with_retry(user_prompt, system_prompt, retries=3):
    """
    ChatGPT APIを呼び出し、JSON形式での応答を試行する
    """
    raw_response = ""  # 外側でキャプチャ
    
    for attempt in range(retries):
        try:
            raw_response = call_chatgpt_api(user_prompt, system_prompt)
            logger.info(f"=== ChatGPT Raw Response (Attempt {attempt + 1}) ===")
            logger.info(raw_response)
            
            # JSONパース試行
            parsed_data = json.loads(raw_response)
            feedback = parsed_data.get("feedback", "")
            grade = parsed_data.get("grade", "")
            
            # グレードバリデーション
            if grade in {"A", "B", "C", "D"} and feedback:
                logger.info(f"=== Valid Response ===")
                logger.info(f"Feedback: {feedback}")
                logger.info(f"Grade: {grade}")
                return {
                    "feedback": feedback,
                    "grade": grade,
                    "raw_response": raw_response,
                    "attempt": attempt + 1
                }
            else:
                logger.warning(f"Invalid grade or missing feedback: grade={grade}, feedback_length={len(feedback)}")
                
        except (ValueError, TypeError, json.JSONDecodeError) as e:
            logger.warning(f"JSON parse error on attempt {attempt + 1}: {e}")
            # 修正3: 追加のAPI呼び出しを削除
    
    # 全ての試行が失敗した場合
    logger.error("All retry attempts failed. Using fallback response.")
    return {
        "feedback": raw_response if raw_response else "AI応答の取得に失敗しました。",
        "grade": None,
        "raw_response": raw_response,
        "attempt": retries
    }

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request):
    user = request.user
    if not user.is_authenticated:
        return Response({'error': 'Authentication required'}, status=403)

    data = request.data
    cycle_session_id = data.get('cycle_session_id')
    question_id = data.get('question_id')
    user_answer = data.get('user_answer')

    # パラメータ必須チェック
    if not all([cycle_session_id, question_id, user_answer]):
        return Response({'error': 'missing parameter'}, status=400)

    # トランザクション全体を包む
    with transaction.atomic():
        try:
            cycle_session = (StraCycleSession.objects
                            .select_for_update()
                            .get(id=cycle_session_id))
        except StraCycleSession.DoesNotExist:
            return Response({'error': '無効なサイクルセッションIDです'}, status=400)

        try:
            question = GrammarQuestion.objects.get(id=question_id)
        except GrammarQuestion.DoesNotExist:
            return Response({'error': '無効な問題IDです'}, status=400)

        # AnswerUnit作成（sessionはnull=True対応済み）
        answer_unit, created = AnswerUnit.objects.update_or_create(
            stra_cycle_session=cycle_session,
            question=question,
            user=user,
            defaults={
                'user_answer': user_answer,
            }
        )

        # GrammarNote取得
        grammar_note = (GrammarNote.objects
                       .filter(subgenre_fk=question.subgenre_fk)
                       .order_by('-version')
                       .first())

        if not grammar_note:
            return Response({'error': '該当する文法ノートが見つかりません'}, status=400)

        user_name = user.line_display_name
        system_prompt = define_system_prompt_for_question(grammar_note, user_name)
        user_prompt = generate_user_prompt(data, question)
        
        # ChatGPT API呼び出し（リトライ機能付き）
        gpt_result = call_gpt_with_retry(user_prompt, system_prompt, retries=3)
        
        feedback_text = gpt_result["feedback"]
        grade = gpt_result["grade"]
        
        # グレードの最終バリデーション
        if grade not in {"A", "B", "C", "D"}:
            grade = None
            logger.warning(f"Invalid grade received: {grade}. Setting to None.")

        # AIFeedback保存
        AIFeedback.objects.update_or_create(
            answer=answer_unit,
            defaults={
                'feedback_text': feedback_text or '未出力'
            }
        )

        # ▲ 必須修正1: StraAnswerEvaluation保存
        if grade:
            from .models import StraAnswerEvaluation  # モデル名修正
            StraAnswerEvaluation.objects.update_or_create(
                answer_unit=answer_unit,  # フィールド名修正
                defaults={
                    "overall_grade": grade,  # フィールド名修正
                    "raw_evaluation_json": gpt_result  # 修正4: dict→JSONField自動シリアライズ
                }
            )
            logger.info(f"Grade {grade} saved for answer_unit {answer_unit.id}")

        # ▲ 必須修正3: COUNT最適化とtarget_questions動的取得
        total_answers = AnswerUnit.objects.filter(
            stra_cycle_session=cycle_session
        ).count()
        
        # ◆ 改善点: ハードコード排除
        target_questions = getattr(cycle_session.stra_session, 'target_cycles', 5)
        
        # サイクル完了チェック
        if total_answers >= target_questions and not cycle_session.completed_at:
            cycle_session.completed_at = timezone.now()
            cycle_session.save(update_fields=["completed_at"])
            logger.info(f"Cycle session {cycle_session.id} completed with {total_answers} answers")

    # 成功時のレスポンス
    response_data = {
        'ai_feedback': feedback_text,
        'answer_unit_id': answer_unit.id,
        'grade': grade,
        'cycle_completed': bool(cycle_session.completed_at),
        'total_answers': total_answers,
        'target_questions': target_questions,
        'message': 'Successfully processed and saved your answer!',
    }
    
    # デバッグ情報（開発時のみ）
    if 'attempt' in gpt_result:  # 修正2: dict判定修正
        response_data['debug_info'] = {
            'attempts_used': gpt_result.get('attempt', 1),
            'raw_response_length': len(gpt_result.get('raw_response', ''))
        }

    return Response(response_data, status=200)


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
    

@api_view(['POST'])
def run_meta_analysis(request):
    """
    DEPRECATED 2025-07-28:
    Tadoku/Stra リファクタに伴いフロントから呼ばれなくなった。
    URL ルーティングからも除外済み。将来不要なら削除。
    """
    session_id = request.data.get("session_id")
    component_id = request.data.get("component_id")

    # ✅ 遅延インポートで循環参照を回避
    from .tasks import run_meta_analysis_task

    thread = Thread(target=run_meta_analysis_task, args=(session_id, component_id))
    thread.start()

    return Response({"message": "メタアナリシス処理をバックグラウンドで開始しました"})



@csrf_exempt
def show_meta_analysis(request):
    """
    DEPRECATED 2025-07-28:
    Tadoku/Stra リファクタに伴いフロントから呼ばれなくなった。
    URL ルーティングからも除外済み。将来不要なら削除。
    """
    if request.method != 'GET':
        return JsonResponse({"error": "Invalid method"}, status=405)

    session_id = request.GET.get("session_id")
    component_id = request.GET.get("component_id")

    if not session_id or not component_id:
        return JsonResponse({"error": "Missing session_id or component_id"}, status=400)

    try:
        session = Session.objects.get(session_id=session_id)
        component = ScheduleComponent.objects.get(component_id=component_id)
    except (Session.DoesNotExist, ScheduleComponent.DoesNotExist):
        return JsonResponse({"error": "Invalid session or component"}, status=404)

    try:
        result = MetaAnalysisResult.objects.get(session=session, component=component)
        return JsonResponse({
            "status": "complete",
            "score": result.score,
            "advice": result.advice
        })
    except MetaAnalysisResult.DoesNotExist:
        return HttpResponse(status=204)
    


class SubmitQuestionClipAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = QuestionClipForGrammarSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            clip = serializer.save()
            return Response({
                "message": "疑問clipが正常に保存されました",
                "clip_id": clip.id
            }, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class QuestionClipListAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        clips = QuestionClipForGrammar.objects.filter(user=user).order_by('-created_at')
        serializer = QuestionClipDetailSerializer(clips, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_review(request):
    answer_unit_id = request.data.get("answer_unit_id")
    if not answer_unit_id:
        return JsonResponse({"error": "answer_unit_id is required"}, status=400)

    try:
        answer_unit = AnswerUnit.objects.get(id=answer_unit_id, user=request.user)
        answer_unit.is_review_target = True
        answer_unit.save()
        return JsonResponse({"message": "Marked for review successfully."})
    except AnswerUnit.DoesNotExist:
        return JsonResponse({"error": "AnswerUnit not found or not owned by user."}, status=404)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_review_questions(request):
    user = request.user
    print("一応呼ばれてますよ")
    MAX_QUESTIONS = 5  # 取得する問題数の上限

    # is_review_target=TrueのAnswerUnitを取得
    answer_units = AnswerUnit.objects.filter(user=user, is_review_target=True, question__isnull=False)

    if not answer_units.exists():
        return JsonResponse([], safe=False)  # 空のリストを返す

    # ランダムにMAX_QUESTIONS件選択
    selected_units = random.sample(list(answer_units), min(MAX_QUESTIONS, len(answer_units)))
    # GrammarQuestionデータの整形
    data = []
    for unit in selected_units:
        question = unit.question
        data.append({
            "id": question.id,
            "question_text": question.question_text,
            "placeholder": "あなたの答えを入力してください",
            "answer": question.answer,
            "submit_endpoint": "/api/ai_writing/submit_answer/",
            "genre": question.genre,
            "subgenre": question.subgenre,
            "difficulty": question.difficulty,
        })
    return JsonResponse(data, safe=False)



@api_view(['GET'])
def list_review_candidates(request):
    user = request.user
    if not user.is_authenticated:
        return Response({"error": "Unauthorized"}, status=401)

    answer_units = AnswerUnit.objects.filter(
        user=user,
        is_review_target=True,
        question__isnull=False
    ).select_related('question').order_by('-created_at')[:50]

    serializer = ReviewCandidateSerializer(answer_units, many=True)
    return Response(serializer.data)







# utils.py
from django.utils import timezone

def local_today():
    """03:00切り上げでの日付取得（夜型学習者対応）"""
    return (timezone.now() - timezone.timedelta(hours=3)).date()


# views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.db import transaction
import random
import uuid

from .models import (
    StraSession, StraCycleSession, GrammarSubgenre, 
    GrammarQuestion, GrammarNote
)
from .serializers import (
    StraSessionSerializer, StraCycleSessionSerializer,
    GrammarQuestionSerializer, GrammarNoteSerializer
)
from .utils import local_today


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_session(request):
    subgenre_id = request.data.get('subgenre_id')
    if not subgenre_id:
        return Response({"error": "subgenre_id is required"}, status=400)

    try:
        material = GrammarSubgenre.objects.get(id=subgenre_id)
    except GrammarSubgenre.DoesNotExist:
        return Response({"error": "Grammar subgenre not found"}, status=404)

    try:
        with transaction.atomic():                                   # ★ 同時 POST 競合対策
        # 1) 未完了セッションがあるかロック付きで取得
            session = (StraSession.objects
                    .select_for_update()
                    .filter(user=request.user,
                            material=material,
                            completed_at__isnull=True)
                    .first())

            if not session:
                # 2) 完了済みセッションが既に存在するか
                completed_exists = StraSession.objects.filter(
                    user=request.user,
                    material=material,
                    completed_at__isnull=False
                ).exists()

                if completed_exists:
                    return Response(
                        {"detail": "本日分の Stra は完了しています。残りの課題に取り組みましょう！"},
                        status=409
                    )

                # 4) ここまで来たら初回なので新規発行
                session = StraSession.objects.create(
                    user=request.user,
                    material=material,
                    session_date=local_today(),
                    target_cycles=5,
                    status=StraSession.StatusChoices.ACTIVE,
                )

            # 5) 未完了 session が確定したので Cycle を取得 / 新規発行
            cycle_session = create_next_cycle_session(session)

        # 3️⃣ 質問 & GrammarNote 取得（トランザクション外で OK）
        questions = build_questions_with_progress(cycle_session)
        grammar_note = get_grammar_note(material)

        return Response({
            "stra_session":  StraSessionSerializer(session).data,
            "stra_cycle_session": StraCycleSessionSerializer(cycle_session).data,
            "questions":     questions,
            "grammar_note":  GrammarNoteSerializer(grammar_note).data if grammar_note else None,
               "user_info": {                              # ★ ここを追加
                 "id":         request.user.id,
                "username":   request.user.username,
                "display_name": getattr(request.user, "line_display_name", "") \
                               or request.user.username,
                },
        }, status=200)

    except ValueError as e:      # create_next_cycle_session が投げる “全周回完了” など
        return Response({'error': str(e)}, status=409)
    except Exception as e:
        import traceback, logging
        logging.exception("start_session unexpected error")
        return Response({'error': f'セッション開始エラー: {str(e)}'}, status=400)

    

def get_or_create_today_session(user, session_date):
    """
    当日のStraSessionを取得または作成
    並列アクセス対策でselect_for_update()使用
    """
    # 未完了セッション確認（排他ロック）
    incomplete_session = (StraSession.objects
        .select_for_update()  # 並列POST対策
        .filter(
            user=user,
            status__in=[StraSession.StatusChoices.ACTIVE, StraSession.StatusChoices.REVIEW],
            session_date=session_date
        ).first())
    
    if incomplete_session:
        return incomplete_session
    
    # 新規セッション作成
    # ダミーのスケジューラーロジック
    material = get_next_material_for_user(user)
    
    stra_session = StraSession.objects.create(
        user=user,
        material=material,
        session_date=session_date,
        target_cycles=5,
        status=StraSession.StatusChoices.ACTIVE
    )
    
    return stra_session


def get_next_material_for_user(user):
    """
    ユーザーの次の学習教材を取得（ダミー実装）
    TODO: 実際のスケジューラー実装時に置き換え
    """
    # ダミーのキュー（実際はDBから取得）
    dummy_queue = [
        {'stra_material_code': 'SV'},
        {'stra_material_code': 'SVO'},
        {'stra_material_code': 'Relative_Clause'},
        {'stra_material_code': 'Past_Perfect'},
    ]
    
    # ユーザーの進行状況確認（完了済みセッション数）
    completed_sessions_count = StraSession.objects.filter(
        user=user,
        status=StraSession.StatusChoices.COMPLETED
    ).count()
    
    # 次の教材を決定
    if completed_sessions_count < len(dummy_queue):
        next_material_code = dummy_queue[completed_sessions_count]['stra_material_code']
    else:
        # 復習モード（ランダム）
        next_material_code = random.choice(dummy_queue)['stra_material_code']
    
    # GrammarSubgenreから取得
    try:
        return GrammarSubgenre.objects.get(code=next_material_code)
    except GrammarSubgenre.DoesNotExist:
        # フォールバック: 最初の教材
        return GrammarSubgenre.objects.first()


def create_next_cycle_session(stra_session):
    """
    次周回のStraCycleSession作成
    競合状態対策でselect_for_update()使用
    """
    next_cycle_index = stra_session.get_next_cycle_index()
    
    if next_cycle_index is None:
        raise ValueError("セッションは既に完了済みです")
    
    # 既存で still_open な Cycle があればそれを返す
    existing_cycle = (StraCycleSession.objects
        .select_for_update()  # 並列POST対策
        .filter(
            stra_session=stra_session,
            cycle_index=next_cycle_index,
            completed_at__isnull=True
        ).first())
    
    if existing_cycle:
        return existing_cycle
    
    # 新規サイクルセッション作成
    cycle_session = StraCycleSession.objects.create(
        stra_session=stra_session,
        cycle_index=next_cycle_index,
        material=stra_session.material,
        session_id=uuid.uuid4().hex,  # ランダムUUID（安全性向上）
        started_at=timezone.now()
    )
    
    return cycle_session


def get_random_questions(material, count=5):
    """
    指定された教材からランダムに問題を取得
    TODO: 大規模データ対応時はプリフェッチまたはランダムID抽出方式に変更
    """
    questions = GrammarQuestion.objects.filter(
        subgenre_fk=material,
        is_active=True
    ).order_by('?')[:count]  # 将来的にパフォーマンス要改善
    
    if questions.count() < count:
        # 問題数が不足している場合の警告
        print(f"Warning: {material.code}の問題数が不足しています ({questions.count()}/{count})")
    
    return questions


def get_grammar_note(material):
    """
    指定された教材のGrammarNoteを取得（軽量化）
    """
    try:
        return (GrammarNote.objects
            .filter(subgenre_fk=material)
            .only('id', 'custom_id', 'title', 'description')  # 必要列のみ取得
            .first())
    except GrammarNote.DoesNotExist:
        return None
    

# ---------- ★ REPLACE: 未完了 Cycle 用の質問ビルダー ----------
from .models import AnswerUnit, GrammarQuestion

def build_questions_with_progress(cycle_session, count=5):
    """
    既回答 AU を必ず含めて、不足分だけ新規問題を補充する
    """
    # ① 既回答 AU 一式を取得
    answered_aus = (cycle_session.answer_units
                    .select_related('question', 'ai_feedback', 'evaluation')
                    .order_by('created_at'))          # 古→新で安定表示

    answered_ids = [au.question_id for au in answered_aus]
    answered_count = len(answered_ids)

    # ② 不足分を抽選（既回答 ID は除外）
    need = max(0, count - answered_count)
    new_questions = []
    if need:
        new_questions = (GrammarQuestion.objects
            .filter(subgenre_fk=cycle_session.material, is_active=True)
            .exclude(id__in=answered_ids)
            .order_by('?')[:need])

    # ③ ペイロードを組み立て
    payload = []

    # ---- 既回答パート ----
    for au in answered_aus:
        q = au.question
        payload.append({
            'id': q.id,
            'question_text': q.question_text,
            'answer': q.answer,
            'genre': q.genre,
            'subgenre_name': getattr(q.subgenre_fk, 'name', None),
            'difficulty': q.difficulty,
            'user_answer': au.user_answer,
            'feedback': (au.ai_feedback.feedback_text
                         if getattr(au, 'ai_feedback', None) else None),
            'grade': (au.evaluation.overall_grade
                      if getattr(au, 'evaluation', None) else None),
            'answered': True,
        })

    # ---- 新規パート ----
    for q in new_questions:
        payload.append({
            'id': q.id,
            'question_text': q.question_text,
            'answer': q.answer,
            'genre': q.genre,
            'subgenre_name': getattr(q.subgenre_fk, 'name', None),
            'difficulty': q.difficulty,
            'user_answer': None,
            'feedback': None,
            'grade': None,
            'answered': False,
        })

    return payload
