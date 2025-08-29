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
    today = today or timezone.localdate()
    print("fetch_or_create_current_assignment_for_user called", today)

    try:
        enr = Enrollment.objects.select_related("state").get(user=user, status="active")
    except ObjectDoesNotExist:
        raise NoActiveEnrollment("Active enrollment not found for user")

    # 1) 未完了を探す（order_index優先→なければ最小order_index）
    da = None
    if getattr(enr, "state", None):
        da = (
            DailyAssignment.objects
            .select_for_update()
            .filter(enrollment=enr, status=DailyAssignment.Status.NOT_DONE,
                    order_index=enr.state.current_order_index)
            .order_by("order_index")
            .first()
        )

    if not da:
        da = (
            DailyAssignment.objects
            .select_for_update()
            .filter(enrollment=enr, status=DailyAssignment.Status.NOT_DONE)
            .order_by("order_index")
            .first()
        )

    if da:
        print("→ 未完了があるのでそれを返す:", da)
        return da

    # 2) 未完了が一つもなければ今日分を新規発行
    print("→ 未完了なし → ensure_next_assignment() で今日分を発行")
    return ensure_next_assignment(enr, today=today)
