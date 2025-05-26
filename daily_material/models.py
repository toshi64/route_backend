from django.db import models
from django.conf import settings
from instant_feedback.models import FinalAnalysis

class CurriculumPlan(models.Model):
    final_analysis = models.OneToOneField(
        FinalAnalysis,
        on_delete=models.CASCADE,
        related_name='curriculum_plan'
    )
    summary_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"CurriculumPlan for Session {self.final_analysis.session.session_id}"

    @property
    def user(self):
        return self.final_analysis.user

    @property
    def session(self):
        return self.final_analysis.session


class CurriculumDay(models.Model):
    curriculum_plan = models.ForeignKey(
        CurriculumPlan,
        on_delete=models.CASCADE,
        related_name='days'
    )
    day = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=100)
    objective = models.TextField()
    focus = models.TextField()
    tag = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('curriculum_plan', 'day')
        ordering = ['curriculum_plan', 'day']

    def __str__(self):
        return f"Day {self.day}: {self.title}"
