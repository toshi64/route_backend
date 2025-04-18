from material_generator.models import Material
from datetime import datetime

def save_to_supabase(material_dict: dict):
    try:
        raw_data = material_dict["data"]

        from material_generator.models import Material
        from datetime import datetime

        Material.objects.create(
            user_id=raw_data["user_id"],
            timestamp=datetime.fromisoformat(raw_data["タイムスタンプ"].replace("Z", "+00:00")),
            user_prompt=material_dict["user_prompt"],
            text=material_dict["text"],
            title=material_dict["title"],
            title_ja=material_dict["title_ja"],
            summary=material_dict["summary"],
            summary_ja=material_dict["summary_ja"],
            raw_data=raw_data
        )

        print("✅ Supabaseへの保存完了")
    except Exception as e:
        print("❌ Supabaseへの保存中にエラーが発生：", e)
