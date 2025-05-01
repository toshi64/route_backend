from django.urls import path
from .views import submit_answer, session_start, session_end, show_analysis, submit_survey_response

urlpatterns = [
    path('submit/', submit_answer, name='submit_answer'),
    path('session_start/', session_start, name='session_start'),
    path('session_end/', session_end), 
    path('show_analysis/', show_analysis, name='show_analysis'), 
    path('survey_submit/', submit_survey_response, name='submit_survey-response'),
]