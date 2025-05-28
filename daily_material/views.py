from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse, Http404, HttpResponseForbidden
from rest_framework.permissions import IsAuthenticated
from .models import CurriculumDay

# 指定された curriculum_day_id に対応する教材コンポーネント（静的・対話型）を取得し、
# フロントエンドで描画可能な JSON 形式で返すビュー関数
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_material_components(request, curriculum_day_id):
    try:
         # curriculum_day_id に該当する CurriculumDay を取得（存在しない場合は 404 を返す）
        day = CurriculumDay.objects.get(id=curriculum_day_id)
    except CurriculumDay.DoesNotExist:
        raise Http404("CurriculumDay not found")
    
     # 自分の教材かどうかをチェック
    if day.user != request.user:
       print("アクセス権のないユーザーです")
       return HttpResponseForbidden("この教材にはアクセスできません")

    # 静的コンポーネント（例：説明テキスト、導入、まとめなど）をリストとして取得
    static_components = list(day.static_components.all())

    # 対話型コンポーネント（例：選択式問題、英作文問題など）をリストとして取得
    interactive_components = list(day.interactive_components.all())

    # 最終的に返すすべてのコンポーネントを格納するリスト
    all_components = []

    # 静的コンポーネントを整形して追加
    for c in static_components:
        all_components.append({
            "order": c.order,
            "type": c.type,
            "props": {
                "text": c.text
            }
        })

    # 対話型コンポーネントを整形して追加
    for c in interactive_components:
        props = {
            "question_text": c.question_text,   # 共通項目：問題文
        }
        # 選択式問題の場合は選択肢と正解も追加
        if c.type == "question_choice":
            props.update({
                "choices": c.choices,
                "correct_choice": c.correct_choice,
            })
         # 英作文問題の場合は模範解答を追加
        elif c.type == "question_writing":
            props.update({
                "model_answer": c.model_answer,
            })

        all_components.append({
            "order": c.order,
            "type": c.type,
            "props": props
        })

    # 表示順 order に基づいて昇順ソート（order: 0 → 1 → 2 ...）
    sorted_components = sorted(all_components, key=lambda x: x["order"])


    # 最終的に JSON でレスポンスを返す
    return JsonResponse({
        "components": sorted_components
    })
