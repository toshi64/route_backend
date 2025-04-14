from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def generate_text(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            print("受け取ったJSONデータ:", data)  # ← ここがRenderのログに出力される
            return JsonResponse({'message': 'データを受け取りました'})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'JSONの読み取りに失敗しました'}, status=400)
    else:
        return JsonResponse({'error': 'POSTメソッドで送ってください'}, status=405)
