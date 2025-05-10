import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    internal_id = models.UUIDField(default=uuid.uuid4, unique=True)

    # 任意フィールド
    full_name = models.CharField(max_length=100, blank=True)
    nickname = models.CharField(max_length=100, blank=True)
    grade = models.CharField(max_length=20, blank=True)

    # LINEログイン用
    line_user_id = models.CharField(max_length=64, null=True, blank=True, unique=True)
    line_display_name = models.CharField(max_length=100, null=True, blank=True)
    line_picture_url = models.URLField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email
