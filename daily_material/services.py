
import json
from instant_feedback.models import FinalAnalysis
from daily_material.models import CurriculumPlan, CurriculumDay, StaticMaterialComponent, InteractiveMaterialComponent
from daily_material.utils.prompts import define_curriculum_plan_prompt, define_material_structure_prompt
from daily_material.utils.call_chatgpt_api import call_chatgpt_api
from daily_material.utils.validators import validate_curriculum_response,validate_daily_material
from daily_material.utils.savers import save_material_components_to_db 

MAX_RETRIES = 5 # バリデーションの再試行の上限回数

 # 総合分析から、自動で６日分の学習コンテンツのカリキュラムを立てる関数。FinalAnalysisの実行後に、そのまま非同期的に呼び出される。
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

                # ここで、生成されたカリキュラムに基づき、教材を生成する関数を非同期で実行する。
                generate_all_daily_materials_for_curriculum_plan(
                    plan_id=curriculum_plan.id,
                    final_analysis=final.analysis_text
                )

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


 # ６日分の教材をカリキュラムから一気に生成する関数。
def generate_all_daily_materials_for_curriculum_plan(plan_id: int, final_analysis: str):

     # ６日分のカリキュラムを統合しているテーブルのID（plan_id）から、６日分の個別カリキュラムのIDを取得する処理。
    curriculum_days = CurriculumDay.objects.filter(curriculum_plan_id=plan_id).order_by("day")

    print(f"\n📆 紐づく CurriculumDay は {curriculum_days.count()} 件です。")
    for day in curriculum_days:
        print(f"\n🛠 Day {day.day}: CurriculumDay ID = {day.id}, Title = {day.title} の教材生成を開始...")
        
        try:
            generate_daily_material_for_each_day(curriculum_id=day.id, final_analysis=final_analysis)
        except Exception as e:
            print(f"❌ Day {day.day} の生成中にエラーが発生しました: {e}")
            continue

    print("\n✅ すべての教材生成処理が完了しました。")


 # カリキュラム1日単位の教材生成を行う関数。UIコンポーネントに使えるデータ素材を作成し、DBに保存。
def generate_daily_material_for_each_day(curriculum_id: int, final_analysis: str):

    # CurriculumDay(1日分のカリキュラム情報をDBから取得)
    try:
        curriculum = CurriculumDay.objects.get(id=curriculum_id)
    except CurriculumDay.DoesNotExist:
        print("❌ CurriculumDay が見つかりませんでした。")
        return

    # カリキュラム情報と、総合分析をUserpromtに統合して定義。
    user_prompt = (
    "これは英語が苦手な高校生のためのカリキュラムの1日分の教材を構成するタスクです。\n"
    "以下のカリキュラム情報と分析文脈を参考に、構造化されたJSON形式で教材を出力してください。\n\n"

    "【カリキュラム情報】\n"
    f"- Day: {curriculum.day}\n"
    f"- Title: {curriculum.title}\n"
    f"- Objective: {curriculum.objective}\n"
    f"- Focus: {curriculum.focus}\n"
    f"- Tag: {curriculum.tag}\n\n"

    "【生徒の状況（FinalAnalysis）】\n"
    "生徒の過去の英作文とその分析から得られた、現在の理解状況と学習課題を以下に示します。\n"
    f"{final_analysis}\n\n"

    "この情報に基づいて、生徒の誤解やつまずきに配慮した教材を出力してください。"
    )
    
    # システムプロンプトを定義
    system_prompt = define_material_structure_prompt()

    # ユーザープロンプトとシステムプロンプトを用いて、ChatGPT APIを呼ぶ。指定した形式に合致しているかをバリデーションし、バリデーションエラーの場合は最大5回繰り返す。
    for attempt in range(1, MAX_RETRIES + 1):
        print(f"\n🚀 試行 {attempt} 回目: ChatGPT呼び出し中...")

        response_text = call_chatgpt_api(user_prompt=user_prompt, system_prompt=system_prompt)

        try:
            parsed_json = json.loads(response_text)

            if validate_daily_material(parsed_json):
                print("✅ バリデーション成功！教材データが有効です。")
                print(json.dumps(parsed_json, indent=2, ensure_ascii=False))

                # 出来上がった教材データを、UIコンポーネント単位に分割してDBに格納。この時、問題データ（インタラクション有）と、説明データ（インタラクション無）は別テーブルで管理する。
                save_material_components_to_db(parsed_json, curriculum_day_id=curriculum.id)

                # TODO: 保存処理を後で追加
                return parsed_json

            else:
                print("⚠️ バリデーションNG（構造エラー）")

        except json.JSONDecodeError:
            print("❌ JSON構文エラー：パースできませんでした。")

        if attempt < MAX_RETRIES:
            print("⏳ 再試行します...")
        else:
            print("❌ 最大試行回数に達しました。処理を中止します。")
            return None