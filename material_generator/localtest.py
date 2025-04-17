import json
import copy
from components.parse_json import parse_json_request
from components.user_prompt_generation import generate_user_prompt
from components.system_prompt_definition import define_system_prompt
from components.chatgpt_generation import call_chatgpt_api
from components.title_generation import generate_title
from components.title_translation import translate_title
from components.summary_generation import generate_summary
from components.summary_translation import translate_summary

# --- 初期素材となるmaterial_dictを定義 ---
material_dict = {
    "id": "abc123",
    "data": {
        "user_id": "abc123",
        "name": "Toshiki",
        "interests": ["tech", "education", "startups"]
    }
}

# ユーザープロンプトを生成
material_dict = generate_user_prompt(material_dict)

# システムプロンプト定義
system_prompt = define_system_prompt()

# --- 教材セットを3本分生成 ---
materials_list = []

for i in range(3):
    print(f"\n--- 教材 {i+1} を生成中 ---")

    temp_dict = copy.deepcopy(material_dict)

    # 本文生成
    temp_dict = call_chatgpt_api(temp_dict, system_prompt)

    # タイトル生成
    temp_dict = generate_title(temp_dict)

    # タイトル翻訳
    temp_dict = translate_title(temp_dict)

    # 要約生成
    temp_dict = generate_summary(temp_dict)

    # 要約翻訳
    temp_dict = translate_summary(temp_dict)

    # 完成教材としてリストに追加
    materials_list.append(temp_dict)

# --- 完成した教材セットを表示 ---
print("\n=== 最終出力された教材セット ===")
for idx, mat in enumerate(materials_list):
    print(f"\n--- 教材 {idx+1} ---")
    print(json.dumps(mat, indent=2, ensure_ascii=False))
