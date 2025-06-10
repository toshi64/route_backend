def validate_meta_analysis(data: dict) -> bool:
    """
    ChatGPTから返されたメタアナリシスJSONの構造を検証する。
    正しい場合は True、不正な場合は False を返す。
    """
    if not isinstance(data, dict):
        print("❌ データは辞書型ではありません。")
        return False

    required_keys = {"score", "advice"}
    if not required_keys.issubset(data.keys()):
        print("❌ 'score' または 'advice' キーが欠けています。")
        return False

    if not isinstance(data["score"], int) or not (0 <= data["score"] <= 100):
        print("❌ 'score' は0〜100の整数である必要があります。")
        return False

    if not isinstance(data["advice"], str) or not data["advice"].strip():
        print("❌ 'advice' は空であってはならず、文字列である必要があります。")
        return False

    if len(data["advice"]) > 100:
        print("❌ 'advice' は100文字以内である必要があります。")
        return False

    return True
