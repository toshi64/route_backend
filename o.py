import os
import django
from datetime import datetime

# Django初期化
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "route_backend.settings")
django.setup()

# 必要な関数のインポート
from material_generator.components.user_prompt_generation import generate_user_prompt
from material_generator.components.system_prompt_definition import define_system_prompt
from material_generator.components.chatgpt_generation import call_chatgpt_api
from material_generator.components.title_generation import generate_title
from material_generator.components.title_translation import translate_title
from material_generator.components.summary_generation import generate_summary
from material_generator.components.summary_translation import translate_summary
from material_generator.components.save_to_supabase import save_to_supabase

# ダミー入力データ（material_dict相当）
dummy_dict = {
    "id": 45621,
    "data": {
        "タイムスタンプ": "2025-04-15T08:08:46.000Z",
        "Q1. 興味のあるテーマを選んでください（複数選択可）": "お金・仕事・ビジネス・副業",
        "Q2. 特に気になる具体的なモノ・人・話題があれば教えてください（自由記述）": "ビジネスマンになりたい",
        "Q3. それについて、どんな内容が読めるとおもしろそうですか？（複数選択可）": "海外での評価・人気の理由",
        " Q4. 英語で読めたら「おっ」と思う内容って、他にありますか？（自由記述・任意）": "ない",
        "Q5. 英語の長さ・難しさについてどう思いますか？（1つ選択）": "短くてやさしいほうがいい（200〜300語）",
        "user_id": 45621
    }
}

# 一連の教材生成 + 保存フロー
material_dict = generate_user_prompt(dummy_dict)
system_prompt = define_system_prompt()
material_dict = call_chatgpt_api(material_dict, system_prompt)
material_dict = generate_title(material_dict)
material_dict = translate_title(material_dict)
material_dict = generate_summary(material_dict)
material_dict = translate_summary(material_dict)

# Supabaseに保存
save_to_supabase(material_dict)

print("✅ ダミー教材の生成・保存が完了しました。")
