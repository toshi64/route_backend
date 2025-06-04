from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_schedule, name='create_schedule'),
    path('list/', views.list_schedule, name='list_schedule'), 
    path('students_list/', views.students_list, name='students_list'),
    path('delete_schedule/<int:schedule_id>/', views.delete_schedule, name='delete_schedule'),
]