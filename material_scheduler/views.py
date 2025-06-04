from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from django.views.decorators.http import require_GET
from rest_framework.response import Response
from .models import Schedule, ScheduleComponent
from django.contrib.auth.decorators import login_required
from datetime import datetime
import json

from accounts.models import CustomUser

@api_view(['POST'])
def create_schedule(request):
    data = request.data
    print("受け取ったデータ:", data)

    try:
        # 各変数に、フロントから渡ってきたJSONの内容を分割して渡す。
        user_id = data["user_id"]
        start_date_str = data["startDate"]
        app = data["app"]
        purpose = data["purpose"]
        range_data = data["range"]

        start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()

        # Scheduleの作成
        schedule = Schedule.objects.create(
            user_id=user_id,
            start_date=start_date,
            mode=data.get("schedule", "once")  # デフォルト: once
        )

        # ScheduleComponentの作成（ジャンルごとに）
        ScheduleComponent.objects.create(
            schedule=schedule,
            app=app,
            purpose=purpose,
            detail=range_data  # JSONFieldにそのまま保存
        )

        return Response({"message": "スケジュールとコンポーネントを作成しました", "schedule_id": schedule.id})

    except Exception as e:
        print("エラー:", e)
        return Response({"error": str(e)}, status=400)


@require_GET
@login_required
def students_list(request):
    user = request.user

    if user.id != 9:
        return HttpResponseForbidden("アクセスが許可されていません")


    users = CustomUser.objects.filter(line_user_id__isnull=False).exclude(line_user_id="")

    result = [
        {
            "id": user.id,
            "name": user.line_display_name or "(名前未設定)"
        }
        for user in users
    ]

    return JsonResponse(result, safe=False)



@require_http_methods(["POST"])
def list_schedule(request):
    try:
        data = json.loads(request.body)
        user_id = data.get("user_id")
        if not user_id:
            return JsonResponse({"error": "user_id is required"}, status=400)

        schedules = Schedule.objects.filter(user__id=user_id).order_by("-start_date")
        response_data = []

        for schedule in schedules:
            components = ScheduleComponent.objects.filter(schedule=schedule)
            component_data = []

            for comp in components:
                component_data.append({
                    "app": comp.app,
                    "purpose": comp.purpose,
                    "detail": comp.detail
                })

            response_data.append({
                "id": schedule.id,
                "start_date": schedule.start_date,
                "mode": schedule.mode,
                "components": component_data
            })

            print(response_data)

        return JsonResponse(response_data, safe=False, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt  # 本番環境では Token 認証と組み合わせましょう
@require_http_methods(["DELETE"])
def delete_schedule(request, schedule_id):
    try:
        schedule = Schedule.objects.get(id=schedule_id)
        # 紐づくScheduleComponentを削除
        ScheduleComponent.objects.filter(schedule=schedule).delete()
        # 本体も削除
        schedule.delete()
        return JsonResponse({'message': '削除が完了しました'}, status=200)
    except Schedule.DoesNotExist:
        return JsonResponse({'error': '指定されたスケジュールが存在しません'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)