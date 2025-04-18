from django.http import JsonResponse
import json
import copy
from django.views.decorators.csrf import csrf_exempt
from .components.parse_json import parse_json_request
from .components.user_prompt_generation import generate_user_prompt
from .components.system_prompt_definition import define_system_prompt
from .components.chatgpt_generation import call_chatgpt_api
from .components.title_generation import generate_title
from .components.title_translation import translate_title
from .components.summary_generation import generate_summary
from .components.summary_translation import translate_summary
from .components.save_to_supabase import save_to_supabase 


@csrf_exempt
def generate_text(request):
    if request.method == 'POST':
        # スコープ①：体験か熟成かを識別（例：ヘッダーに識別子を含める）
        source = request.headers.get("X-Source-Type", "unknown")

        if source == "GAS":
            material_dict = parse_json_request(request)
            if material_dict is None:
                return JsonResponse({'error': 'JSONパースに失敗しました'}, status=400)

            material_dict = generate_user_prompt(material_dict)
            system_prompt = define_system_prompt()
            
            material_dict = call_chatgpt_api(material_dict, system_prompt)
            material_dict = generate_title(material_dict)
            material_dict = translate_title(material_dict)
            material_dict = generate_summary(material_dict)
            material_dict = translate_summary(material_dict)

            save_to_supabase(material_dict)

            return JsonResponse({"material": material_dict}, json_dumps_params={"ensure_ascii": False})

        return JsonResponse({'error': '不正なソースタイプです'}, status=400)