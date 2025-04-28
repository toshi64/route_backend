from django.urls import path
from .views import submit_answer

urlpatterns = [
    path('submit/', submit_answer, name='submit_answer'),
]