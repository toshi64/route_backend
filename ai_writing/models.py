from django.db import models
from instant_feedback.models import Session
from accounts.models import CustomUser
from material_scheduler.models import ScheduleComponent

class GrammarQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    custom_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.DecimalField(max_digits=3, decimal_places=1)  # 例: 1.0
    created_by = models.CharField(max_length=100)
    question_text = models.TextField()
    genre = models.CharField(max_length=100)
    subgenre = models.CharField(max_length=100)
    level = models.IntegerField()
    type = models.CharField(max_length=100)
    difficulty = models.IntegerField()
    importance = models.IntegerField()
    answer = models.TextField()
    source = models.CharField(max_length=100)
    is_active = models.BooleanField()

class GrammarNote(models.Model):
    custom_id = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.CharField(max_length=10, default='1.0')
    created_by = models.CharField(max_length=100)

    subgenre = models.CharField(max_length=100)  # 例: "SV", "SVO" など
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Markdownで記述された解説本文")

    class Meta:
        ordering = ['created_at']  # 古い順。新しい順なら ['-created_at']

    def __str__(self):
        return f"{self.subgenre}: {self.title}"


class AnswerUnit(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    question = models.ForeignKey(GrammarQuestion, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    user_answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    component = models.ForeignKey(ScheduleComponent, on_delete=models.SET_NULL, null=True, blank=True)

class AIFeedback(models.Model):
    answer = models.OneToOneField(AnswerUnit, on_delete=models.CASCADE, related_name='ai_feedback')
    feedback_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class MetaAnalysisResult(models.Model):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    component = models.ForeignKey(ScheduleComponent, on_delete=models.CASCADE)
    
    score = models.IntegerField()
    advice = models.CharField(max_length=100)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("session", "component")  # 1セッション×1コンポーネントに対し1つだけ記録




class QuestionClipForGrammar(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    # 実際の出題内容に基づいたclipなので、AnswerUnitは必須
    answer_unit = models.ForeignKey(AnswerUnit, on_delete=models.CASCADE)

    # GrammarQuestionも保持（検索・表示用途）
    grammar_question = models.ForeignKey(GrammarQuestion, on_delete=models.SET_NULL, null=True, blank=True)

    # セッション文脈（分析用）
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True)

    # カリキュラム構造との接続
    schedule_component = models.ForeignKey(ScheduleComponent, on_delete=models.SET_NULL, null=True, blank=True)

    # 疑問clipのタイトルと内容
    title = models.CharField(max_length=255)
    content = models.TextField()

    # 投稿日時
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Clip from {self.user} - {self.title[:20]} ({self.created_at})"
