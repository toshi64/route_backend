# assignment/services.py
from datetime import date
from django.utils import timezone
from accounts.models import Enrollment
from assignment.models import EnrollmentState, DailyAssignment
from assignment.services import _DATA  # 仮カリキュラム




# ==========================
# 個別コンポーネントビルダー
# ==========================



def build_message(raw):
    now = timezone.localtime()  # サーバーの現在時刻（TZ注意）

    hour = now.hour
    if 4 <= hour < 11:
        greeting = "greeting_morning"
    elif 11 <= hour < 17:
        greeting = "greeting_afternoon"
    else:
        greeting = "greeting_evening"

    # 既に今日アクセスして学習しているかどうかの判定
    today = str(now.date())
    assignments = raw.get("assignments", [])
    today_done = any(
        a["target_date"] == today and a["status"] == "completed"
        for a in assignments
    )

    if today_done:
        status = "already_studied"
    else:
        status = "first_access"

    return {
        "type": greeting,
        "status": status,
    }

from datetime import date

def build_today(raw):
    """今日の学習状況を返す（案1ロジックを反映）"""
    today_str = str(date.today())
    assignments = raw["assignments"]

    # 今日の課題
    today_assignment = next(
        (a for a in assignments if a["target_date"] == today_str),
        None
    )

    # 今日分が存在し、すでに完了しているなら → その情報を返す
    if today_assignment and today_assignment["status"] == "completed":
        assignment = today_assignment

    # 今日分が存在しない → 前日の持ち越し（target_date < today の未完了）
    elif not today_assignment:
        assignment = next(
            (a for a in reversed(assignments) if a["target_date"] < today_str and a["status"] != "completed"),
            None
        )

    # 今日分が存在するが未完了なら → 今日分を返す
    else:
        assignment = today_assignment

    # fallback: 課題が全くない場合
    if not assignment:
        return {
            "stra": {"completed": False, "progress": {"current": 0, "total": 0}},
            "tadoku": {"completed": False, "progress": {"current": 0, "total": 0}},
        }

    # StraとTadokuの状況を構築
    result = {}
    for item in assignment["items"]:
        if item["component"] == "stra":
            result["stra"] = {
                "completed": item["status"] == "completed",
                "progress": {
                    "current": item["stra_session"]["completed_cycles"] if item["stra_session"] else 0,
                    "total": item["stra_session"]["target_cycles"] if item["stra_session"] else 0,
                },
                "material_name": item["stra_session"]["material_name"] if item["stra_session"] else None,
            }

        elif item["component"] == "tadoku":
            result["tadoku"] = {
                "completed": item["status"] == "completed",
                "progress": {
                    "current": item["tadoku_session"]["completed_cycles"] if item["tadoku_session"] else 0,
                    "total": item["tadoku_session"]["target_cycles"] if item["tadoku_session"] else 0,
                },
                "material_title": item["tadoku_session"]["material_title"] if item["tadoku_session"] else None,
                "total_word_count": item["tadoku_session"]["total_word_count"] if item["tadoku_session"] else None,
            }

    return result


def build_progress(raw):
    """全体の進捗状況"""
    total_days = len(_DATA)
    completed_days = sum(1 for a in raw["assignments"] if a["status"] == "completed")
    streak_days = 0  # 後述のstreakと重複するのでゼロで返す

    return {
        "completed_days": completed_days,
        "total_days": total_days,
        "overall_percent": round(completed_days / total_days * 100, 1) if total_days else 0,
    }


def build_streak(raw):
    streak = 0
    today_str = str(date.today())

    # 今日の分は未完了でも無視してカウントを始める
    assignments = [a for a in raw["assignments"] if a["target_date"] < today_str]

    for a in reversed(assignments):
        if not a["completed_at"]:
            break
        if str(a["target_date"]) == str(a["completed_at"])[:10]:
            streak += 1
        else:
            break

    return {"streak_days": streak}

def build_calendar(raw):
    """カレンダー形式の学習状況"""
    today = str(date.today())
    calendar = []

    for a in raw["assignments"]:
        if a["completed_at"] is None and a["target_date"] < today:
            status = "missed"
        elif a["completed_at"] and a["target_date"] < str(a["completed_at"])[:10]:
            status = "delayed"
        elif a["completed_at"] and a["target_date"] == str(a["completed_at"])[:10]:
            status = "ontime"
        elif a["target_date"] == today:
            status = "today"
        else:
            status = "future"

        calendar.append({
            "day": a["target_date"],
            "status": status,
        })

    return calendar


# ==========================
# Summaryビルダー
# ==========================
def build_summary(raw):
    return {
        "message": build_message(raw),
        "today": build_today(raw),
        "progress": build_progress(raw),
        "streak": build_streak(raw),
        "calendar": build_calendar(raw),
    }


# ==========================
# Rawデータ取得（既存関数を流用）
# ==========================
def get_dashboard_raw_context(user):
    """Dashboard用: 生データ全部返す"""
    enrollment = Enrollment.objects.get(user=user, status="active")
    enrollment_state = EnrollmentState.objects.get(enrollment=enrollment)

    assignments = (
        DailyAssignment.objects
        .filter(enrollment=enrollment)
        .prefetch_related("items", "items__stra_session", "items__tadoku_session")
        .order_by("target_date")
    )

    return {
        "enrollment": {
            "id": enrollment.id,
            "curriculum_id": enrollment.curriculum_id,
        },
        "enrollment_state": {
            "current_order_index": enrollment_state.current_order_index,
            "last_assigned_at": str(enrollment_state.last_assigned_at) if enrollment_state.last_assigned_at else None,
        },
        "curriculum_count": len(_DATA),
        "assignments": [
            {
                "id": a.id,
                "target_date": str(a.target_date),
                "status": a.status,
                "completed_at": str(a.completed_at) if a.completed_at else None,
                "items": [
                    {
                        "id": i.id,
                        "component": i.component,
                        "status": i.status,
                        "stra_session": (
                            {
                                "id": i.stra_session.id,
                                "completed_cycles": i.stra_session.completed_cycles,
                                "target_cycles": i.stra_session.target_cycles,
                                "material_name": i.stra_session.material.name if i.stra_session and i.stra_session.material else None,
                            } if i.stra_session else None
                        ),
                        "tadoku_session": (
                            {
                                "id": i.tadoku_session.id,
                                "completed_cycles": i.tadoku_session.completed_cycles,
                                "target_cycles": i.tadoku_session.target_cycles,
                                "material_title": i.tadoku_session.material.title if i.tadoku_session and i.tadoku_session.material else None,
                                "total_word_count": i.tadoku_session.material.total_word_count if i.tadoku_session and i.tadoku_session.material else None,
                            } if i.tadoku_session else None
                        ),

                    }
                    for i in a.items.all()
                ],
            }
            for a in assignments
        ],
    }
