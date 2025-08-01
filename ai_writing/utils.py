from django.utils import timezone

def local_today():
    """03:00切り上げでの日付取得（夜型学習者対応）"""
    return (timezone.now() - timezone.timedelta(hours=3)).date()