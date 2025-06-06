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
