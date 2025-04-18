from django.db import models

class Material(models.Model):
    user_id = models.IntegerField()
    timestamp = models.DateTimeField()

    # 教材生成結果（構造が安定）
    user_prompt = models.TextField()
    text = models.TextField()
    title = models.CharField(max_length=255)
    title_ja = models.CharField(max_length=255)
    summary = models.TextField()
    summary_ja = models.TextField()

    # アンケートの生データ（JSONで柔軟に扱う）
    raw_data = models.JSONField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user_id} - {self.title}"
