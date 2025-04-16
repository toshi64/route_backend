from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt
from .components.parse_json import parse_json_request
from .components.user_prompt_generation import generate_user_prompt
from .components.system_prompt_definition import define_system_prompt
from .components.chatgpt_generation import generate_text

@csrf_exempt
def generate_text(request):
    if request.method == 'POST':
        # スコープ①：体験か熟成かを識別（例：ヘッダーに識別子を含める）
        source = request.headers.get("X-Source-Type", "unknown")

        if source == "GAS":  # 体験用として処理
            data = parse_json_request(request)
            if data is None:
                return JsonResponse({'error': 'JSONパースに失敗しました'}, status=400)

            prompt = generate_user_prompt(data)
            print("生成されたユーザープロンプト：\n", prompt)  # レンダーログに出力

            system_prompt = define_system_prompt()
            print("システムプロンプト：\n", system_prompt)

            generated_text = generate_text(prompt, system_prompt)

            if generated_text:
             return JsonResponse({"generated_text": generated_text})
            else:
             return JsonResponse({"error": "ChatGPT API呼び出しに失敗しました"}, status=500)
    
    return JsonResponse({'error': 'POSTメソッドで送信してください'}, status=405)
