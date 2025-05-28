from django.urls import path
from .views import get_material_components

urlpatterns = [
    path('<int:curriculum_day_id>/', get_material_components, name='get_material_components'),
]