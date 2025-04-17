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
            
            materials_list = []
            for i in range(3):
                print(f"--- 教材 {i+1} を生成中 ---")

                temp_dict = copy.deepcopy(material_dict)
                temp_dict = call_chatgpt_api(temp_dict, system_prompt)
                temp_dict = generate_title(temp_dict)
                temp_dict = translate_title(temp_dict)
                temp_dict = generate_summary(temp_dict)
                temp_dict = translate_summary(temp_dict)

                materials_list.append(temp_dict)

            return JsonResponse({"materials": materials_list}, json_dumps_params={"ensure_ascii": False})
