from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def generate_text(request):
    if request.method == 'POST':
        try:
            # リクエストボディをデコード
            body = request.body.decode('utf-8')
            print("デコード後:", body)

            # JSONのパース
            data = json.loads(body)
            print("受信データ:", data)

            # レスポンスを返す
            return JsonResponse({'message': 'データを受信しました', 'data': data})
        except json.JSONDecodeError as e:
            print("JSONパースエラー:", str(e))
            return JsonResponse({'error': 'JSONパース失敗', 'details': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'POSTメソッドで送信してください'}, status=405)

