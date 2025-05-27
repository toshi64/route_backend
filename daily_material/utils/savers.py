from daily_material.models import StaticMaterialComponent, InteractiveMaterialComponent

def save_material_components_to_db(parsed_json: list, curriculum_day_id: int):
    """
    構造化された教材JSONを受け取り、カリキュラムの日付IDに紐づけてDBに保存する。
    """
    from daily_material.models import CurriculumDay

    try:
        curriculum_day = CurriculumDay.objects.get(id=curriculum_day_id)
    except CurriculumDay.DoesNotExist:
        print(f"❌ CurriculumDay ID {curriculum_day_id} が見つかりませんでした。")
        return

    for i, component in enumerate(parsed_json):
        comp_type = component.get("type")
        props = component.get("props", {})

        if comp_type in {"theme_intro", "explanation", "summary"}:
            # インタラクションなし（説明系）
            StaticMaterialComponent.objects.create(
                curriculum_day=curriculum_day,
                type=comp_type,
                text=props.get("text", ""),
                order=i
            )
        elif comp_type == "question_choice":
            # 選択問題
            InteractiveMaterialComponent.objects.create(
                curriculum_day=curriculum_day,
                type=comp_type,
                question_text=props.get("question_text", ""),
                choices=props.get("choices", []),
                correct_choice=props.get("correct_choice", ""),
                model_answer=None,
                order=i
            )
        elif comp_type == "question_writing":
            # 自由記述問題
            InteractiveMaterialComponent.objects.create(
                curriculum_day=curriculum_day,
                type=comp_type,
                question_text=props.get("question_text", ""),
                model_answer=props.get("model_answer", ""),
                choices=None,
                correct_choice=None,
                order=i
            )
        else:
            print(f"⚠️ 未対応のtype: {comp_type} が含まれていました（スキップされました）")

    print("✅ 教材コンポーネントの保存が完了しました。")
