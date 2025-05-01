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
    session_id = models.CharField(max_length=100, unique=True)
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
    

class MetaAnalysis(models.Model):
    answer = models.OneToOneField(
        'StudentAnswerUnit',
        on_delete=models.CASCADE,
        related_name='meta_analysis'
    )
    meta_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"MetaAnalysis for AnswerUnit {self.answer.id}"


class SurveyResponse(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='survey_responses')
    created_at = models.DateTimeField(auto_now_add=True)

    question_1 = models.TextField()
    answer_1 = models.TextField()
    question_2 = models.TextField()
    answer_2 = models.TextField()
    question_3 = models.TextField()
    answer_3 = models.TextField()
    question_4 = models.TextField()
    answer_4 = models.TextField()
    question_5 = models.TextField()
    answer_5 = models.TextField()
    question_6 = models.TextField()
    answer_6 = models.TextField()

    def __str__(self):
        return f"Survey by {self.user} for session {self.session.session_id}"