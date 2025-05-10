from django.urls import path
from . import views

urlpatterns = [
    path('callback', views.line_login_callback, name='line_login_callback'),
    # ここにWebhookやPushなど今後追加できます
]