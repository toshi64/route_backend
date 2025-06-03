import uuid
from django.db import models
from django.conf import settings

class Schedule(models.Model):
    # 外部キー：ユーザー
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="schedules")
    
    # UUID型のスケジュールID（主キーとして明示）
    schedule_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    
    # スケジュール開始日
    start_date = models.DateField()
    
    # モード（daily_for_one_week / once など）
    mode = models.CharField(max_length=50, choices=[
        ('daily_for_one_week', '1週間毎日'),
        ('once', '一回のみ'),
    ])
    
    # 作成日時（自動記録）
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Schedule({self.user_id}, {self.mode}, {self.start_date})"


import uuid
from django.db import models
from django.conf import settings
from django.contrib.postgres.fields import JSONField  # Django 4.0以降なら models.JSONField を使えます

class ScheduleComponent(models.Model):
    # 外部キー：Schedule（多対一）
    schedule = models.ForeignKey("Schedule", on_delete=models.CASCADE, related_name="components")
    
    # UUID型のコンポーネントID
    component_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True, db_index=True)
    
    # アプリの種類（例：grammar, ai_writing, ...）
    app = models.CharField(max_length=50)
    
    # 学習目的（例：review, test, new, ...）
    purpose = models.CharField(max_length=50)

    # detail（ジャンルなどを含む柔軟な構造。JSONで保存）
    detail = models.JSONField()  # Django 3.1+。PostgreSQL必須。

    # 作成日時
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Component({self.app}, {self.purpose}, {self.schedule_id})"