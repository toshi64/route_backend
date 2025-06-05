# run_generate_all_materials.py

import os, sys
import django
import asyncio

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) 
# 1. Djangoプロジェクト設定を読み込み
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "route_backend.settings")
django.setup()

# 2. 対象関数をインポート（正確なモジュールパスに修正）
from ai_writing.models import GrammarQuestion
import random

def make_questions_from_schedule_component(schedule_component: dict):
    all_matched_questions = []

    # genre→subgenre→isActiveでソートしていく。
    for genre, subgenres in schedule_component.items():
        # 有効な問題のみフィルター（is_active=True）
        matched = GrammarQuestion.objects.filter(
            genre=genre,
            subgenre__in=subgenres,
            is_active=True
        )
        all_matched_questions.extend(list(matched))

     # ランダム化して5問取得する。
    selected_questions = random.sample(all_matched_questions, min(5, len(all_matched_questions)))

    # 必要な情報のみ抽出してJSONに整形
    result = []
    for q in selected_questions:
        result.append({
            "id": q.id,
            "genre": q.genre,
            "subgenre": q.subgenre,
            "question_text": q.question_text,
            "answer": q.answer,
        })

    print(result)
    return result


if __name__ == "__main__":
    test_schedule = {
        "文型": ["SV", "SVO"],
        "不定詞": ["to + 動詞"]
    }
    result = make_questions_from_schedule_component(test_schedule)
    for i, r in enumerate(result, 1):
        print(f"{i}. {r['question_text']} ({r['genre']} / {r['subgenre']}) → {r['answer']}")


# python ai_writing/o.py