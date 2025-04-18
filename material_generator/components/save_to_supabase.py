from material_generator.models import Material
from datetime import datetime

def save_to_supabase(material_dict: dict):
    """生成された教材データをSupabaseに保存する関数"""
    
    # raw_dataはJSONFieldにそのまま渡す
    raw_data = material_dict["data"]

    # SupabaseのMaterialテーブルに保存
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

    print(f"✅ user_id {raw_data['user_id']} の教材をSupabaseに保存しました。")
