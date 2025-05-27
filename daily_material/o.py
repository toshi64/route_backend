# run_generate_all_materials.py

import os, sys
import django
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
# 1. Djangoプロジェクト設定を読み込み
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "route_backend.settings")
django.setup()

# 2. 対象関数をインポート（正確なモジュールパスに修正）
from daily_material.services import generate_all_daily_materials_for_curriculum_plan
from instant_feedback.models import FinalAnalysis

def main():
    plan_id = 4
    final = FinalAnalysis.objects.get(session__id=955)

    generate_all_daily_materials_for_curriculum_plan(
        plan_id=plan_id,
        final_analysis=final.analysis_text
    )

if __name__ == "__main__":
    main()


# python daily_material/o.py