from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .components.parse_json import parse_json_request

@csrf_exempt
def generate_text(request):
    if request.method == 'POST':
        # スコープ①：体験か熟成かを識別（例：ヘッダーに識別子を含める）
        source = request.headers.get("X-Source-Type", "unknown")

        if source == "GAS":  # 体験用として処理
            data = parse_json_request(request)
            if data is None:
                return JsonResponse({'error': 'JSONパースに失敗しました'}, status=400)

            print("新しい dict 形式で体験用データを受け取りました:", data)
            return JsonResponse({
                'message': '新しい dict 形式で体験用データを受け取りました',
                'data': data
            })

        else:
            return JsonResponse({
                'error': 'このソースは未対応です（GAS以外）',
                'source': source
            }, status=400)
    
    return JsonResponse({'error': 'POSTメソッドで送信してください'}, status=405)
