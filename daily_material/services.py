
import json
from instant_feedback.models import FinalAnalysis
from daily_material.models import CurriculumPlan, CurriculumDay
from daily_material.utils.prompts import define_curriculum_plan_prompt
from daily_material.utils.call_chatgpt_api import call_chatgpt_api
from daily_material.utils.validators import validate_curriculum_response

MAX_RETRIES = 5 # バリデーションの再試行の上限回数

def generate_curriculum_from_final_analysis(session_id: int):
    try:
        final = FinalAnalysis.objects.get(session__id=session_id)   # FinalAnalysisを引数のsession_idから取得
    except FinalAnalysis.DoesNotExist:
        print("❌ FinalAnalysis が見つかりませんでした。")
        return

    user_prompt = final.analysis_text    # ユーザープロンプトつくる。そのままstrを突っ込むだけ。
    system_prompt = define_curriculum_plan_prompt()  # システムプロンプトつくる。prompts.pyに少し抽象化して処理を書いてある。複数のシステムプロンプトファイルを一元的に管理したいため。

    for attempt in range(1, MAX_RETRIES + 1):   # DBの形式に合うJSON形式に、ChatGPTが合わせて生成しているかを、検品する処理。変だったらやり直し。
        print(f"\n🚀 試行 {attempt} 回目: ChatGPT呼び出し中...")

        response_text = call_chatgpt_api(user_prompt=user_prompt, system_prompt=system_prompt)

        # JSON構文チェック → バリデーションチェック
        try:
            parsed_json = json.loads(response_text)
            if validate_curriculum_response(parsed_json):   # これはvalidators.pyに定義されたJSONの型などの規則に適うかを、booleanで判定する処理。これがTrue🟰バリデーションOK。
                print("✅ バリデーション成功！保存処理に進みます。")
                print(parsed_json)

                # 1. CurriculumPlan を作成
                curriculum_plan = CurriculumPlan.objects.create(
                    final_analysis=final,
                    summary_text=parsed_json["summary"]
                )

                # 2. CurriculumDay を6件作成
                for day_data in parsed_json["days"]:
                    CurriculumDay.objects.create(
                        curriculum_plan=curriculum_plan,
                        day=day_data["day"],
                        title=day_data["title"],
                        objective=day_data["objective"],
                        focus=day_data["focus"],
                        tag=day_data["tag"]
                    )

                print("📥 カリキュラム保存完了！")



                return  # このケースなら処理完了。リトライなし。
            else:
                print(f"⚠️ バリデーションNG（構造エラー）") # バリデーションエラー。リトライ。
        except json.JSONDecodeError:
            print("❌ JSON構文エラー。パースできませんでした。")    # バリデーション以前に構文エラー（余計な点や説明が混ざっているなど）。リトライ。

        # リトライ判定
        if attempt < MAX_RETRIES:
            print("⏳ 再試行します...")
        else:
            print("❌ 最大試行回数に達しました。処理を中止します。")
            return
