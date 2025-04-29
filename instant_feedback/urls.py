from django.urls import path
from .views import submit_answer, session_start

urlpatterns = [
    path('submit/', submit_answer, name='submit_answer'),
    path('session_start/', session_start, name='session_start'),
]