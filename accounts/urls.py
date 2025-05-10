# accounts/urls.py
from django.urls import path
from .views import signup_view, login_view, logout_view, me_view, get_csrf_token, profile_update

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('me/', me_view, name='me'),
    path('csrf/', get_csrf_token, name='get_csrf_token'),
    path('profile/', profile_update, name='profile_update'),
]