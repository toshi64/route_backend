from django.urls import path
from . import views

app_name = 'tadoku'

urlpatterns = [
    # 教材データ取得API
    path('material/', views.get_material_data, name='get_material_data'),
    path('session/start/', views.start_session, name='start_session'),
    path('session/<uuid:session_id>/complete-cycle/', views.complete_cycle, name='complete_cycle'),
    path('session/<uuid:session_id>/stats/', views.get_session_stats, name='get_session_stats'),
]