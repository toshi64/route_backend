from django.urls import path
from . import views

app_name = 'tadoku'

urlpatterns = [
    # 教材データ取得API
    path('material/', views.get_material_data, name='get_material_data'),
]