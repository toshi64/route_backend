# run_test_insert.py

import os
import django

# Djangoの設定を読み込む
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "route_backend.settings")  # ←プロジェクト名に合わせて修正
django.setup()

# モデルや関数をインポート
from material_generator.models import Material
from datetime import datetime

def insert_test_material():
    Material.objects.create(
        user_id=999,
        timestamp=datetime.fromisoformat("2025-04-15T08:08:46+00:00"),
        user_prompt="このプロンプトはテストです。",
        text="This is a test article generated for demonstration purposes.",
        title="The Rise of the Testers",
        title_ja="テスターたちの時代",
        summary="A summary of the test article goes here.",
        summary_ja="これはテスト記事の要約です。",
        raw_data={
            "Q1": "テスト・開発・エンジニアリング",
            "Q2": "とにかく動くものを作りたい",
            "Q3": "海外の開発事情",
            "Q4": "特になし",
            "Q5": "短くてやさしい方がいい",
            "user_id": 999,
            "タイムスタンプ": "2025-04-15T08:08:46.000Z"
        }
    )

    print("✅ テストデータをSupabaseに保存しました！")

# 関数実行
insert_test_material()
