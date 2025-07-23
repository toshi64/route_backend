# tadoku/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .models import Material, MaterialSection

@require_http_methods(["POST"])
def get_material_data(request):
    """
    教材IDを受け取って、教材のメタデータとセクションデータをJSONで返す
    """
    try:
        # POSTデータからmaterial_idを取得
        data = json.loads(request.body)
        material_id = data.get('material_id')
        
        if not material_id:
            return JsonResponse({
                'error': 'material_id is required'
            }, status=400)
        
        # 教材マスターデータを取得
        try:
            material = Material.objects.get(id=material_id)
        except Material.DoesNotExist:
            return JsonResponse({
                'error': f'Material with id {material_id} not found'
            }, status=404)
        
        # 関連するセクションデータを取得（section_numberでソート）
        sections = MaterialSection.objects.filter(
            material=material
        ).order_by('section_number')
        
        # レスポンス用データを構築
        response_data = {
            'material_meta': {
                'id': material.id,
                'title': material.title,
                'subgenre': material.subgenre,
                'total_word_count': material.total_word_count,
                'total_sections': material.total_sections,
                'created_at': material.created_at.isoformat(),
                'updated_at': material.updated_at.isoformat()
            },
            'sections': []
        }
        
        # セクションデータを追加
        for section in sections:
            section_data = {
                'section': section.section_number,
                'text': section.text,
                'translation': section.translation,
                'word_count': section.word_count,
                'audio_url': section.audio_url
            }
            response_data['sections'].append(section_data)
        
        return JsonResponse(response_data, status=200)
        
    except json.JSONDecodeError:
        return JsonResponse({
            'error': 'Invalid JSON format'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'error': f'Internal server error: {str(e)}'
        }, status=500)

