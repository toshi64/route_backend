# apps/orchestrator/services.py
from __future__ import annotations
from typing import Optional
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

from accounts.models import Enrollment
from assignment.models import DailyAssignment  
from assignment.services import ensure_next_assignment

class NoActiveEnrollment(Exception):
    """ユーザーに active Enrollment が無い場合のシグナル"""
    pass

@transaction.atomic
def fetch_or_create_current_assignment_for_user(user, *, today=None) -> Optional[DailyAssignment]:
    """
    1) ユーザーの active Enrollment を取得
    2) 未完了(NOT_DONE)の DailyAssignment があれば「最優先の1件」を返す
       - state.current_order_index に一致する行があればそれを優先
       - それが無ければ未完了の最小 order_index を返す（遅延がある場合の救済）
    3) それも無ければ ensure_next_assignment を呼んで新規作成（なければ None）
    """
    today = today or timezone.localdate()

    try:
        # Enrollment は accounts アプリ側
        enr = Enrollment.objects.select_related("state").get(user=user, status="active")
    except ObjectDoesNotExist:
        raise NoActiveEnrollment("Active enrollment not found for user")

    # 2-a) 進捗ポインタを優先（あるなら）
    if getattr(enr, "state", None):
        da = (
            DailyAssignment.objects
            .select_for_update()
            .filter(
                enrollment=enr,
                status=DailyAssignment.Status.NOT_DONE,
                order_index=enr.state.current_order_index,
            )
            .order_by("order_index")
            .first()
        )
        if da:
            return da

    # 2-b) 未完了の最小 order（遅延があれば一番手前から）
    da = (
        DailyAssignment.objects
        .select_for_update()
        .filter(enrollment=enr, status=DailyAssignment.Status.NOT_DONE)
        .order_by("order_index")
        .first()
    )
    if da:
        return da

    # 3) 未完了が無い → 新規を用意（state lazy 初期化は assignment.services に委譲）
    return ensure_next_assignment(enr, today=today)
