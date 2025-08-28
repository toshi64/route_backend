# dashboard/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .services import get_dashboard_raw_context, build_summary

@api_view(["GET"])
@permission_classes([IsAuthenticated])
def dashboard_summary(request):
    """
    Dashboard Summary API
    → 今日の学習 / 全体の進捗 / 連続記録 / カレンダー
    """
    user = request.user
    raw = get_dashboard_raw_context(user)
    summary = build_summary(raw)
    return Response(summary)
