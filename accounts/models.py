import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    internal_id = models.UUIDField(default=uuid.uuid4, unique=True)

    # 新しく追加するフィールド
    full_name = models.CharField(max_length=100, blank=True)     # 氏名（任意）
    nickname = models.CharField(max_length=100, blank=True)      # ニックネーム（任意）
    grade = models.CharField(max_length=20, blank=True)          # 学年（任意）

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
