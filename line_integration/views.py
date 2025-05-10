# line_integration/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .services import get_line_tokens, get_line_profile

@api_view(['GET'])
def line_login_callback(request):
    code = request.query_params.get('code')
    state = request.query_params.get('state')  # CSRF対策に使う場合は検証処理を追加

    try:
        token_data = get_line_tokens(code)
        access_token = token_data['access_token']
        profile = get_line_profile(access_token)
    except Exception as e:
        return Response({'error': str(e)}, status=500)

    return Response({
        'message': 'LINEログイン成功',
        'line_user_id': profile.get('userId'),
        'display_name': profile.get('displayName'),
        'picture_url': profile.get('pictureUrl'),
    })
