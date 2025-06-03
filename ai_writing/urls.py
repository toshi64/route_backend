from django.urls import path
from . import views

urlpatterns = [
    path('session_start/', views.session_start, name='session_start'),
    path('make_question/', views.make_question, name='make_question'),
]