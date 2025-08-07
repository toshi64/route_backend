#!/usr/bin/env python
"""
Stra Session が 5 周で completed になるか
── 手動で DB にダミーデータを流し込む簡易テスト

$ python auto_test.py
"""

import os
import django
from django.utils import timezone

# 1) プロジェクト設定をロード
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "route_backend.settings")
django.setup()

# 2) 必要なモデルを import
from django.contrib.auth import get_user_model
from ai_writing.models import (
    StraSession, StraCycleSession,
    AnswerUnit, GrammarQuestion, GrammarSubgenre
)

def main():
    user = get_user_model().objects.get(id=9)       # ← テスト用ユーザー
    material = GrammarSubgenre.objects.get(id=14)  # ← SVC の例

    # StraSession を確保
    session, _ = StraSession.objects.get_or_create(
        user=user,
        material=material,
        completed_at__isnull=True,
        defaults={
            "session_date": timezone.now().date(),
            "target_cycles": 5,
            "status": "active",
        })

    # 5 周分をダミーで完了させる
    for idx in range(1, 6):
        cycle, _ = StraCycleSession.objects.get_or_create(
            stra_session=session,
            cycle_index=idx,
            defaults={"material": material,
                      "started_at": timezone.now()}
        )

        qs = list(GrammarQuestion.objects.filter(subgenre_fk=material)[:5])
        for q in qs:
            AnswerUnit.objects.get_or_create(
                stra_cycle_session=cycle,
                question=q,
                user=user,
                defaults={"user_answer": "dummy"}
            )

        cycle.completed_at = timezone.now()
        cycle.save()                   # 親セッションの progress がここで更新

    # 結果確認
    session.refresh_from_db()
    print("completed_cycles:", session.completed_cycles)
    print("status:",           session.status)
    print("completed_at:",     session.completed_at)

    assert session.completed_cycles == 5
    assert session.status == "completed"
    print("✅ テスト合格 — Stra Session 完了ロジック OK")

if __name__ == "__main__":
    main()
