# prepare_stra_test.py
import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "route_backend.settings")
django.setup()

from ai_writing.models import StraSession, StraCycleSession

def prepare(session_id: str):
    try:
        # セッションを取得
        session = StraSession.objects.get(id=session_id)
        session.completed_cycles = 4
        session.save()

        # CycleSession を新規作成
        cycle = StraCycleSession.objects.create(
            stra_session=session,
            material=session.material,
            cycle_index=4,
            # 他に必須フィールドがあればここで埋める
        )

        print(f"✅ Session {session_id} を completed_cycles=4 に設定しました")
        print(f"✅ StraCycleSession {cycle.id} を cycle_index=4 で作成しました")

    except StraSession.DoesNotExist:
        print(f"❌ Session {session_id} が見つかりません")

if __name__ == "__main__":
    # 実行時に書き換え
    prepare("84f15e99-e6b4-4b52-a0f4-93a4d1dbfcac")
