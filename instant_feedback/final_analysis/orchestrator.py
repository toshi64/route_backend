from line_integration.services import send_line_text_to_user
from .context_waiter import wait_for_meta_analysis
from accounts.models import CustomUser

from rest_framework.response import Response
from ..components.call_chatgpt_api import call_chatgpt_api
from ..components.define_meta_meta_systemprompt import define_meta_meta_systemprompt

from ..models import Session, FinalAnalysis


def run_analysis(session_id, user_id):
    """
    指定されたセッションとユーザーに対して、英作文診断の最終分析を非同期で実行する関数。

    主な処理内容：
    1. 対象ユーザー情報を取得
    2. LINEで「分析開始通知」を送信
    3. メタ分析が全て完了するまで待機（ポーリング）
    4. 完了した分析データを元に、GPTで最終フィードバックを生成
    5. FinalAnalysis テーブルに分析結果を保存（既存データがあれば更新）
    6. LINEで「診断完了通知＋結果メッセージ」を送信
    7. 練習用カリキュラム生成の非同期関数を呼び出して、このスコープは終了。

    ※ 本関数は通常、APIエンドポイントから `threading.Thread` によって非同期実行される。
    ※ HTTPレスポンスは返さず、完全にバックグラウンドで処理される想定。
    """

    user = CustomUser.objects.get(id=user_id)

    send_line_text_to_user(
        user_id,
        "英作文、お疲れ様でした！\nまもなくこちらのチャットに分析の結果をお送りします。\n少々お待ちください。"
    )

    context_data = wait_for_meta_analysis(session_id, user)

    userprompt = context_data["formatted_prompt"]

    systemprompt = define_meta_meta_systemprompt(context_data)

    gpt_result = call_chatgpt_api({"user_prompt": userprompt}, systemprompt)

    final_feedback = gpt_result["ai_feedback"]

    session = Session.objects.get(session_id=session_id, user=user)

    final_analysis, _ = FinalAnalysis.objects.update_or_create(
        session=session,
        user=user,
        defaults={"analysis_text": final_feedback}
    )

    message_text = f"診断が完了しました！\n\n--- 分析結果 ---\n{final_analysis.analysis_text.strip()}"

    send_line_text_to_user(user.id, message_text)

    from daily_material.utils.trigger import trigger_curriculum_generation
    trigger_curriculum_generation(session.id)