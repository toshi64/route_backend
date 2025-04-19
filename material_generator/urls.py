from django.urls import path
from . import views

urlpatterns = [
    path('generate/', views.generate_text, name='generate_text'),
    path('material/<int:material_id>/', views.get_material, name='get_material'),
]
