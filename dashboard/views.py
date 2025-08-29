# dashboard/views.py
from rest_framework.decorators import api_view, permission_classes
from orchestrator.services import fetch_or_create_current_assignment_for_user
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.utils import timezone

from .services import get_dashboard_raw_context, build_summary

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """
    Dashboard Summary API
    → 今日の学習 / 全体の進捗 / 連続記録 / カレンダー
    """
    user = request.user
    today = timezone.localdate()

    # ★ Orchestrator経由で ensure_next_assignment を必ず通す
    da = fetch_or_create_current_assignment_for_user(user, today=today)
    print(da)
    raw = get_dashboard_raw_context(user, ensure_assignment=da)
    summary = build_summary(raw)
    return Response(summary)
