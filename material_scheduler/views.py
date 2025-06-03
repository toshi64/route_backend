from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Schedule, ScheduleComponent
from datetime import datetime
import json

@csrf_exempt
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
