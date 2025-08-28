# assignment/services.py
from __future__ import annotations
from typing import Optional, Dict, Any, List
from django.db import transaction
from django.utils import timezone

from accounts.models import Enrollment
from .models import EnrollmentState, DailyAssignment, DailyAssignmentItem

# ============================================================
# TEMP: カリキュラムプロバイダ（テスト用。後でDB実装に差し替え）
# ============================================================
_DATA: List[Dict[str, Any]] = [
    {
        "id": 1,
        "curriculum_id": "cur_beg_2025_08",
        "order_index": 1,
        "stra_material_id": 17,
        "tadoku_material_id": 7,
    },
    {
        "id": 2,
        "curriculum_id": "cur_beg_2025_08",
        "order_index": 2,
        "stra_material_id": 18,
        "tadoku_material_id": 7,
    },
    {
        "id": 3,
        "curriculum_id": "cur_beg_2025_08",
        "order_index": 3,
        "stra_material_id": 19,
        "tadoku_material_id": 7,
    },
]

def fetch_queue_item(curriculum_id: str, order_index: int) -> Optional[Dict[str, Any]]:
    """
    カリキュラム定義の取得（いまは直書き）。将来はここをDB参照に差し替える。
    見つからなければ None（＝その先は無い/終了）を返す。
    """
    for r in _DATA:
        if r["curriculum_id"] == curriculum_id and r["order_index"] == order_index:
            return r
    return None

# ============================================================
# 本体: アサインメント生成
# ============================================================
@transaction.atomic
def ensure_next_assignment(
    enrollment: Enrollment,
    *,
    today=None,
) -> Optional[DailyAssignment]:
    """
    この Enrollment について「次にやるべき1行」を“存在させて”返す（無ければ作る／あれば既存を返す）。
    - EnrollmentState は lazy 初期化（なければ current_order_index=1 で作る）
    - 既存の同 order 行が未完なら新規は作らない（それを返す）
    - カリキュラムが尽きていれば None
    """
    today = today or timezone.localdate()

    # ① State（進捗ポインタ）をロックして取得/初期化
    state, _ = EnrollmentState.objects.select_for_update().get_or_create(
        enrollment=enrollment, defaults={"current_order_index": 1}
    )

    # ② 次の教材（カリキュラム項目）
    item = fetch_queue_item(enrollment.curriculum_id, state.current_order_index)
    if not item:
        return None  # コース終了

    # ③ 親 DailyAssignment を idempotent に用意（同 order は1回だけ）
    latest = DailyAssignment.objects.filter(enrollment=enrollment).order_by("-order_index").first()

    # target_date の決定ロジック
    if latest:
        if latest.status == DailyAssignment.Status.COMPLETED:
            if latest.target_date == today:
                # 今日分が既に完了 → 明日分を発行
                return latest
            elif latest.target_date < today:
                # 遅延完了 → 今日分を発行
                next_target_date = today
            else:
                # 将来日付の assignment が既にある → そのまま返す
                return latest
        else:
            # 未完了 → 既存を返す
            return latest
    else:
        # 初回
        next_target_date = today

    da, created = DailyAssignment.objects.get_or_create(
        enrollment=enrollment,
        order_index=state.current_order_index,
        defaults={
            "curriculum_id": enrollment.curriculum_id,
            "target_date": next_target_date,  # ← 修正ポイント
            "status": DailyAssignment.Status.NOT_DONE,
        },
    )

    # ④ 子アイテム（stra/tadoku）も揃える（idempotent）
    _ensure_item(da, DailyAssignmentItem.Component.STRA,   item.get("stra_material_id"))
    _ensure_item(da, DailyAssignmentItem.Component.TADOKU, item.get("tadoku_material_id"))

    if created:
        state.last_assigned_at = timezone.now()
        state.save(update_fields=["last_assigned_at"])

    return da


def _ensure_item(
    da: DailyAssignment,
    component: str,
    material_id: Optional[int],
) -> DailyAssignmentItem:
    item, created = DailyAssignmentItem.objects.get_or_create(
        assignment=da,
        component=component,
        defaults={
            "material_id": material_id,
            "status": DailyAssignmentItem.Status.NOT_DONE,
        },
    )

    # material_id の補完（既存が NULL のときだけ入れる：冪等）
    if item.material_id is None and material_id is not None:
        item.material_id = material_id
        item.save(update_fields=["material_id"])

    # 安全弁：コンポーネントに合わないセッションFKが残っていたら消す（更地なら不要だが一応）
    if component == DailyAssignmentItem.Component.STRA:
        if item.tadoku_session_id is not None:
            item.tadoku_session = None
            item.save(update_fields=["tadoku_session"])
    elif component == DailyAssignmentItem.Component.TADOKU:
        if item.stra_session_id is not None:
            item.stra_session = None
            item.save(update_fields=["stra_session"])

    return item




@transaction.atomic
def complete_assignment_item(item_id: int, user):
    """
    指定された DailyAssignmentItem を完了にし、
    DailyAssignment や EnrollmentState の進行も更新する。
    """
    try:
        # 1) アイテムを取得 & ロック
        item = (DailyAssignmentItem.objects
                .select_for_update()
                .select_related("assignment__enrollment")
                .get(id=item_id, assignment__enrollment__user=user))
        
        print(f"[DEBUG] Got item={item.id}, status={item.status}")

        # 既に完了なら何もしない（冪等性保証）
        if item.status == DailyAssignmentItem.Status.COMPLETED:
            print(f"[DEBUG] Item {item.id} already completed")
            return item

        # 2) アイテムを完了にする
        item.status = DailyAssignmentItem.Status.COMPLETED
        item.completed_at = timezone.now()
        item.save(update_fields=["status", "completed_at"])
        print(f"[DEBUG] Marked item {item.id} as COMPLETED")

        assignment = item.assignment

        # 3) DailyAssignment 内の他アイテムも確認
        all_done = assignment.items.filter(
            status=DailyAssignmentItem.Status.NOT_DONE
        ).count() == 0

        if all_done and assignment.status != DailyAssignment.Status.COMPLETED:
            # DailyAssignment を完了にする
            assignment.status = DailyAssignment.Status.COMPLETED
            assignment.completed_at = timezone.now()
            assignment.save(update_fields=["status", "completed_at"])

            # 4) EnrollmentState の current_order_index を進める
            state = assignment.enrollment.state
            state.current_order_index += 1
            state.last_assigned_at = timezone.now()
            state.save(update_fields=["current_order_index", "last_assigned_at"])

        return item

    except DailyAssignmentItem.DoesNotExist:
        raise ValueError("AssignmentItem not found or does not belong to this user")