
def validate_curriculum_response(data: dict) -> bool:
    """
    ChatGPTから返されたカリキュラムJSONの構造を検証する。
    正しい場合は True、不正な場合は False を返す。
    """
    required_keys = {"summary", "days"}
    required_day_fields = {"day", "title", "objective", "focus", "tag"}

    if not isinstance(data, dict):
        print("❌ データは辞書型ではありません。")
        return False

    if not required_keys.issubset(data.keys()):
        print("❌ 'summary' または 'days' キーが欠けています。")
        return False

    if not isinstance(data["summary"], str) or not data["summary"].strip():
        print("❌ 'summary' が空か、文字列ではありません。")
        return False

    days = data["days"]
    if not isinstance(days, list) or len(days) != 6:
        print("❌ 'days' はリストで、要素が6個である必要があります。")
        return False

    for i, day in enumerate(days, start=1):
        if not isinstance(day, dict):
            print(f"❌ day {i} の要素が辞書ではありません。")
            return False
        if not required_day_fields.issubset(day.keys()):
            print(f"❌ day {i} に必要なフィールドがすべて存在していません。")
            return False
        if not isinstance(day["day"], int) or day["day"] != i:
            print(f"❌ day {i} の 'day' フィールドが整数で {i} になっていません。")
            return False
        for field in ["title", "objective", "focus", "tag"]:
            if not isinstance(day[field], str) or not day[field].strip():
                print(f"❌ day {i} の '{field}' が空か、文字列ではありません。")
                return False

    return True
