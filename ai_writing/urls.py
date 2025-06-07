from django.urls import path
from . import views

urlpatterns = [
    path('session_start/', views.session_start, name='session_start'),
    path('make_question/', views.make_question, name='make_question'),
    path('get_questions_from_component_id/', views.get_questions_from_component_id, name='get_questions_from_component_id'),
    path('submit_answer/', views.submit_answer, name='submit_answer'),
    path('show_progress/', views.show_progress, name='show_progress'),
    path('get_grammar_note/', views.get_grammar_note, name='get_grammar_note'),
]