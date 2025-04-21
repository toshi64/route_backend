from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'              # ログインIDとして使うフィールド
    REQUIRED_FIELDS = ['username']        # createsuperuser時に必要なフィールド（Django都合）

    def __str__(self):
        return self.email
