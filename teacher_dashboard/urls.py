from django.urls import path
from .views import student_summary_view

urlpatterns = [
    path('student_summary/', student_summary_view, name='student_summary_view'),
]