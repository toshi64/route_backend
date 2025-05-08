# load_eijakushindan_questions.py

import os
import django
import json

# Django設定を読み込む
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "route_backend.settings")  # ←プロジェクト名に変更
django.setup()

from instant_feedback.models import EijakushindanQuestion

# JSONファイルの読み込み
with open("data/eijakushindan_questions.json", "r", encoding="utf-8") as f:
    data = json.load(f)

# データをモデルに変換して一括登録
questions = [
    EijakushindanQuestion(
        question_text=item["question_text"],
        model_answer=item["model_answer"]
    )
    for item in data
]

EijakushindanQuestion.objects.bulk_create(questions)

print(f"{len(questions)} 件の問題をDBに登録しました。")
