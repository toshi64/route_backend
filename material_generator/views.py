from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def generate_text(request):
    if request.method == 'POST':
        try:
            body_str = request.body.decode('utf-8')
            print("Raw body string:", body_str)

            data = json.loads(body_str)
            print("Parsed JSON:", data)
            return JsonResponse({'message': 'データを受け取りました'})
        except Exception as e:
            print("例外:", str(e))
            return JsonResponse({'error': 'JSONの読み取りに失敗しました', 'details': str(e)}, status=400)
    else:
        return JsonResponse({'error': 'POSTメソッドで送ってください'}, status=405)
