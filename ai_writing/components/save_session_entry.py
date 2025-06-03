from django.utils import timezone
from instant_feedback.models import (
    Session,
)


def save_session_entry(user, session_id):
    """
    Supabase上のinstant_feedback_sessionテーブルに
    user_id, session_id, started_at を保存する関数
    """
    Session.objects.create(
        user=user,
        session_id=session_id,
        started_at=timezone.now()
    )
