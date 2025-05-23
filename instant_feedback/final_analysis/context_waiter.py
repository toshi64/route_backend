import time
from ..components.get_context_data import get_context_data

MAX_RETRIES = 5
RETRY_INTERVAL_SEC = 10
EXPECTED_TOTAL = 5 # 今回は常に5問出題

def wait_for_meta_analysis(session_id, user):
    for attempt in range(1, MAX_RETRIES + 2):
        context_data = get_context_data(session_id=session_id, user=user)
        counts = context_data.get("field_counts", {})
        total = counts.get("total", 0)
        completed = counts.get("meta_analysis", 0)

        print(f"[{attempt}] 現在の進捗: total={total}, completed={completed}")

        # 出題がまだ済んでいない場合は待つ
        if total < EXPECTED_TOTAL:
            print(f"[未出題] まだ全問題（{EXPECTED_TOTAL}問）が出題されていません。リトライ待機中。")
            time.sleep(RETRY_INTERVAL_SEC)
            continue

        # メタ分析が完了していない場合も待つ
        if completed < EXPECTED_TOTAL:
            print(f"[未完了] メタ分析 {completed}/{EXPECTED_TOTAL} 件。リトライ待機中。")
            time.sleep(RETRY_INTERVAL_SEC)
            continue

        # 完了判定
        print(f"[分析完了] メタ分析 {completed}/{EXPECTED_TOTAL} 件完了（リトライ {attempt - 1} 回）")
        return context_data

    print(f"[タイムアウト] メタ分析が {MAX_RETRIES * RETRY_INTERVAL_SEC}秒以内に完了しませんでした。")
    return context_data  # 最終取得値を返す（諦め）
