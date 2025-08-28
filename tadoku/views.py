# tadoku/views.py
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
from .models import Material, MaterialSection
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import date
from .models import TadokuSession, Material

from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
import json

from .models import TadokuSession, TadokuSessionStats
from django.db import transaction
from orchestrator.services import fetch_or_create_current_assignment_for_user
from assignment.models import DailyAssignmentItem
from assignment.services import complete_assignment_item

import logging
logger = logging.getLogger(__name__)

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



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from datetime import date
from .models import TadokuSession, Material, TadokuSessionStats

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_session(request):
    try:
        with transaction.atomic():
            # 0) orchestrator 起点：ユーザーだけで「今やるべき1日の行」を取得/生成
            da = fetch_or_create_current_assignment_for_user(request.user)
            if not da:
                return Response({"detail": "カリキュラムはすべて完了しました。"},
                                status=status.HTTP_200_OK)

            # 1) 当日の TADOKU アイテムを取得
            tadoku_item = (da.items
                           .select_for_update()
                           .filter(component=DailyAssignmentItem.Component.TADOKU)
                           .first())
            if not tadoku_item or tadoku_item.material_id is None:
                return Response({"error": "TADOKUの教材が未設定です"},
                                status=status.HTTP_409_CONFLICT)

            try:
                material = Material.objects.get(id=tadoku_item.material_id)
            except Material.DoesNotExist:
                return Response({"error": "Material not found"},
                                status=status.HTTP_404_NOT_FOUND)
            
            # 2) 既存セッション再利用 or 新規作成
            if not tadoku_item.tadoku_session:
                session = TadokuSession.objects.create(
                    user=request.user,
                    learning_context_id=f"legacy-{material.id}",
                    material=material,
                    session_date=date.today(),
                    target_cycles=5,
                    status='active',
                    started_at=timezone.now(),
                )
                tadoku_item.tadoku_session = session
                if not tadoku_item.started_at:
                    tadoku_item.started_at = timezone.now()
                tadoku_item.save(update_fields=["tadoku_session", "started_at"])
            else:
                session = tadoku_item.tadoku_session

            if tadoku_item.status == DailyAssignmentItem.Status.COMPLETED:
                return Response({
                    "detail": "Tadokuは完了済みです。未完了の課題に取り組んでください。"
                }, status=status.HTTP_200_OK)

        
        # 統計データ取得
        session_stats = TadokuSessionStats.objects.filter(
            session=session
        ).order_by('cycle_number')
        
        # 統計データをシリアライズ
        stats_data = []
        for stat in session_stats:
            stats_data.append({
                "cycle_number": stat.cycle_number,
                "sound_only_count": stat.sound_only_count,
                "text_count": stat.text_count,
                "translation_count": stat.translation_count,
                "total_pages": stat.total_pages,
                "sound_ratio": round(stat.sound_ratio, 1),
                "text_ratio": round(stat.text_ratio, 1),
                "translation_ratio": round(stat.translation_ratio, 1),
                "created_at": stat.created_at.isoformat(),
                "updated_at": stat.updated_at.isoformat()
            })
        
        # 統計サマリー計算
        stats_summary = {
            "total_cycles_with_stats": session_stats.count(),
            "total_sound_only": sum(stat.sound_only_count for stat in session_stats),
            "total_text": sum(stat.text_count for stat in session_stats),
            "total_translation": sum(stat.translation_count for stat in session_stats),
            "total_pages_studied": sum(stat.total_pages for stat in session_stats)
        }
        
        # 全体の比率計算
        if stats_summary["total_pages_studied"] > 0:
            stats_summary.update({
                "overall_sound_ratio": round(
                    (stats_summary["total_sound_only"] / stats_summary["total_pages_studied"]) * 100, 1
                ),
                "overall_text_ratio": round(
                    (stats_summary["total_text"] / stats_summary["total_pages_studied"]) * 100, 1
                ),
                "overall_translation_ratio": round(
                    (stats_summary["total_translation"] / stats_summary["total_pages_studied"]) * 100, 1
                )
            })
        else:
            stats_summary.update({
                "overall_sound_ratio": 0.0,
                "overall_text_ratio": 0.0,
                "overall_translation_ratio": 0.0
            })
        
        # レスポンス構築
        return Response({
            "session": {
                "session_id": str(session.id),
                "learning_context_id": session.learning_context_id,
                "target_cycles": session.target_cycles,
                "completed_cycles": session.completed_cycles,
                "current_cycle": session.current_cycle,
                "status": session.status,
                "session_date": session.session_date.isoformat(),
                "progress_percentage": session.progress_percentage,
                "started_at": session.started_at.isoformat() if session.started_at else None,
                "completed_at": session.completed_at.isoformat() if session.completed_at else None
            },
            "material": {
                "id": material.id,
                "title": material.title,
                "subgenre": getattr(material, 'subgenre', ''),
                "total_word_count": getattr(material, 'total_word_count', 0),
                "total_sections": material.sections.count(),
                "sections": [
                    {
                        "section": section.section_number,
                        "text": section.text,
                        "translation": section.translation,
                        "word_count": section.word_count,
                        "audio_url": section.audio_url
                    }
                    for section in material.sections.all()
                ]
            },
            "statistics": {
                "cycle_stats": stats_data,
                "summary": stats_summary
            },
            "context": {
                "last_accessed": session.updated_at.isoformat()
            }
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {"error": f"Internal server error: {str(e)}"}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


from django.contrib.auth import get_user_model
User = get_user_model()

@api_view(['PATCH'])
@permission_classes([])
# @permission_classes([IsAuthenticated])
def complete_cycle(request, session_id):
   """
   周回完了時のSTTデータを記録するAPI
   """
   try:
       request.user = User.objects.get(id=9)
       # セッション取得
       session = get_object_or_404(TadokuSession, id=session_id, user=request.user)
       
       # リクエストデータ取得
       data = request.data
       sound_only_count = data.get('sound_only_count', 0)
       text_count = data.get('text_count', 0)
       translation_count = data.get('translation_count', 0)
       total_pages = data.get('total_pages', 0)
       
       # バリデーション
       if total_pages != (sound_only_count + text_count + translation_count):
           return Response({
               'error': 'total_pages must equal sum of individual counts'
           }, status=status.HTTP_400_BAD_REQUEST)
       
       # 次の周回数を自動計算
       next_cycle = session.completed_cycles + 1
       
       # STTデータを保存
       stats = TadokuSessionStats.objects.create(
           session=session,
           cycle_number=next_cycle,
           sound_only_count=sound_only_count,
           text_count=text_count,
           translation_count=translation_count,
           total_pages=total_pages,
       )
       
       # セッションの completed_cycles を更新
       session.completed_cycles = next_cycle
       session.save()

        # セッションの完了を、assignmentアプリに通知。こちらでdaily assignmentが更新される。
       if session.completed_cycles >= session.target_cycles:
        item = session.assignment_items.first()  # 1:1想定
        if item and item.status != "completed":
            complete_assignment_item(item_id=item.id, user=request.user)
            logger.info(f"Tadoku completed → AssignmentItem {item.id} marked completed")

       
       # レスポンス
       return Response({
           'message': 'Cycle completed successfully',
           'stats': {
               'id': str(stats.id),
               'cycle_number': stats.cycle_number,
               'sound_only_count': stats.sound_only_count,
               'text_count': stats.text_count,
               'translation_count': stats.translation_count,
               'total_pages': stats.total_pages,
               'sound_ratio': stats.sound_ratio,
               'text_ratio': stats.text_ratio,
               'translation_ratio': stats.translation_ratio,
           },
           'session': {
               'completed_cycles': session.completed_cycles,
               'current_cycle': session.current_cycle,
               'progress_percentage': session.progress_percentage,
           }
       }, status=status.HTTP_200_OK)
       
   except Exception as e:
       return Response({
           'error': f'An error occurred: {str(e)}'
       }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
   


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_session_stats(request, session_id):
    """
    指定されたセッションのSTT統計データを取得するAPI
    """
    try:
        # セッション取得（ユーザー認証も含む）
        session = get_object_or_404(TadokuSession, id=session_id, user=request.user)
        
        # セッションに紐づく全ての統計データを取得（周回順でソート）
        stats = TadokuSessionStats.objects.filter(session=session).order_by('cycle_number')
        
        # データが存在しない場合
        if not stats.exists():
            return Response({
                'session_id': str(session_id),
                'stats': [],
                'message': 'No statistics found for this session'
            }, status=status.HTTP_200_OK)
        
        # レスポンス用データ構築
        stats_data = []
        for stat in stats:
            stats_data.append({
                'cycle_number': stat.cycle_number,
                'sound_only_count': stat.sound_only_count,
                'text_count': stat.text_count,
                'translation_count': stat.translation_count,
                'total_pages': stat.total_pages,
                'sound_ratio': round(stat.sound_ratio, 1),
                'text_ratio': round(stat.text_ratio, 1),
                'translation_ratio': round(stat.translation_ratio, 1),
                'completed_at': stat.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        # セッション情報も含めて返す
        response_data = {
            'session_id': str(session_id),
            'session_info': {
                'target_cycles': session.target_cycles,
                'completed_cycles': session.completed_cycles,
                'current_cycle': session.current_cycle,
                'progress_percentage': session.progress_percentage,
                'material_id': session.material.id
            },
            'stats': stats_data,
            'total_stats_count': len(stats_data)
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'An error occurred: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)