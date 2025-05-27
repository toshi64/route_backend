
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



def validate_daily_material(data: list) -> bool:
    """
    ChatGPTから返された教材JSONの構造を検証する。
    正しい場合は True、不正な場合は False を返す。
    """

    allowed_types = {
        "theme_intro",
        "explanation",
        "question_choice",
        "question_writing",
        "summary"
    }

    if not isinstance(data, list):
        print("❌ データは配列（リスト）である必要があります。")
        return False

    if not (5 <= len(data) <= 10):
        print("⚠️ コンポーネント数は5〜10個が推奨されています（現在: {}）".format(len(data)))

    for i, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            print(f"❌ コンポーネント {i} は辞書型である必要があります。")
            return False

        # type が存在していて有効か
        if "type" not in item or item["type"] not in allowed_types:
            print(f"❌ コンポーネント {i} の 'type' が無効または存在しません。")
            return False

        # props の存在と型チェック
        if "props" not in item or not isinstance(item["props"], dict):
            print(f"❌ コンポーネント {i} に 'props' が存在しないか、辞書型ではありません。")
            return False

        # typeごとのpropsバリデーション
        t = item["type"]
        props = item["props"]

        if t in {"theme_intro", "explanation", "summary"}:
            if "text" not in props or not isinstance(props["text"], str) or not props["text"].strip():
                print(f"❌ コンポーネント {i}（{t}）の 'text' フィールドが不正です。")
                return False

        elif t == "question_choice":
            if not all(k in props for k in ["question_text", "choices", "correct_choice"]):
                print(f"❌ コンポーネント {i}（{t}）の必須propsが不足しています。")
                return False
            if not isinstance(props["question_text"], str) or not props["question_text"].strip():
                print(f"❌ コンポーネント {i} の 'question_text' が不正です。")
                return False
            if not isinstance(props["choices"], list) or not all(isinstance(c, str) for c in props["choices"]):
                print(f"❌ コンポーネント {i} の 'choices' が文字列リストではありません。")
                return False
            if props["correct_choice"] not in props["choices"]:
                print(f"❌ コンポーネント {i} の 'correct_choice' が 'choices' 内に存在しません。")
                return False

        elif t == "question_writing":
            if not all(k in props for k in ["question_text", "model_answer"]):
                print(f"❌ コンポーネント {i}（{t}）の必須propsが不足しています。")
                return False
            if not isinstance(props["question_text"], str) or not props["question_text"].strip():
                print(f"❌ コンポーネント {i} の 'question_text' が不正です。")
                return False
            if not isinstance(props["model_answer"], str) or not props["model_answer"].strip():
                print(f"❌ コンポーネント {i} の 'model_answer' が不正です。")
                return False

    return True
