from django.urls import path
from . import views

urlpatterns = [
    path('session_start/', views.session_start, name='session_start'),
    path('make_question/', views.make_question, name='make_question'),
    path('get_questions_from_component_id/', views.get_questions_from_component_id, name='get_questions_from_component_id'),
    path('submit_answer/', views.submit_answer, name='submit_answer'),
    path('show_progress/', views.show_progress, name='show_progress'),
    path('get_grammar_note/', views.get_grammar_note, name='get_grammar_note'),
    path('run_meta_analysis/', views.run_meta_analysis, name='run_meta_analysis'),
    path('show_meta_analysis/', views.show_meta_analysis, name='show_meta_analysis'),
    path('show_session_history/', views.show_session_history, name='show_session_history'),
    path('question_clips/submit/', views.SubmitQuestionClipAPIView.as_view(), name='submit_question_clip'),
    path('question_clips/', views.QuestionClipListAPIView.as_view(), name='question-clip-list'),
    path('add_to_review/', views.add_to_review, name='add_to_review'),
    path('get_review_questions/', views.get_review_questions, name='get_review_questions'), 
    path('list_review_candidates/', views.list_review_candidates),
]