# run_generate_all_materials.py

import os, sys
import django
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
# 1. Djangoプロジェクト設定を読み込み
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "route_backend.settings")
django.setup()

# 2. 対象関数をインポート（正確なモジュールパスに修正）
from daily_material.services import generate_daily_material_for_each_day
from instant_feedback.models import FinalAnalysis

def main():
    curriculum_id = 19  # ← あなたのテスト用の CurriculumDay のIDに差し替えてください
    final = FinalAnalysis.objects.get(session__id=955)

    generate_daily_material_for_each_day(
        curriculum_id=curriculum_id,
        final_analysis=final.analysis_text
    )

if __name__ == "__main__":
    main()


# python daily_material/p.py