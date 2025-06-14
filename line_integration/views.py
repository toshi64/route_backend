from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth import get_user_model, login
from .services import get_line_tokens, get_line_profile
from django.shortcuts import redirect

User = get_user_model()

@api_view(['GET'])
def line_login_callback(request):
    code = request.query_params.get('code')
    state = request.query_params.get('state')  # 任意のCSRF対策など

    try:
        # ① アクセストークンとプロフィール取得
        token_data = get_line_tokens(code)
        access_token = token_data['access_token']
        profile = get_line_profile(access_token)

        line_user_id = profile.get('userId')
        display_name = profile.get('displayName')
        picture_url = profile.get('pictureUrl')

        # ② LINE IDでユーザーを取得 or 新規作成
        user, created = User.objects.get_or_create(
            line_user_id=line_user_id,
            defaults={
                "email": f"line_{line_user_id}@noemail.route",  # ←ダミーemail
                "username": f"line_{line_user_id}",
                "line_display_name": display_name,
                "line_picture_url": picture_url,
            }
        )

        # ③ プロフィールの更新（初回登録後 or 毎回更新したいなら）
        user.line_display_name = display_name
        user.line_picture_url = picture_url
        user.save()

        # ④ Djangoセッションにログイン
        login(request, user)

        # 🔽 リダイレクト先を条件で切り替える
        if state == "xyz123":
            redirect_url = "https://app.route-web.com/first_diagnosis/ai_writing"
        else:
            # state にURLが入っていた場合はそこへ戻す（念のため allowlist チェックも検討）
            redirect_url = state or "https://app.route-web.com/"  # fallback

        return redirect(redirect_url)

    except Exception as e:
        return Response({"error": str(e)}, status=500)