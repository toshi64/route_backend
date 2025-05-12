from django.urls import path
from .views import submit_answer, session_start, session_end, start_analysis,show_analysis, submit_survey_response, make_question, progress_check_view

urlpatterns = [
    path('submit/', submit_answer, name='submit_answer'),
    path('session_start/', session_start, name='session_start'),
    path('session_end/', session_end), 
    path('start_analysis/', start_analysis, name='start_analysis'), 
    path('show_analysis/', show_analysis, name='show_analysis'), 
    path('survey_submit/', submit_survey_response, name='submit_survey-response'),
    path('make_question/', make_question, name='make_question'),
    path('progress/', progress_check_view, name='progress_check_view'),
]