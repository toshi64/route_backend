from django.db import models
from django.conf import settings  # ユーザーモデル参照

class Session(models.Model):
    """
    英作文チャレンジ（問題集合）を表すモデル
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Session {self.id} by {self.user}"

class StudentAnswerUnit(models.Model):
    """
    1問の問題文・生徒の回答・AI添削結果のワンセットを表すモデル
    """
    session = models.ForeignKey(
        Session,
        on_delete=models.CASCADE,
        related_name='student_answer_units'
    )
    question_text = models.TextField()
    user_answer = models.TextField()
    ai_feedback = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"AnswerUnit {self.id} for Session {self.session.id}"
