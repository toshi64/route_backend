# accounts/serializers.py
from rest_framework import serializers
from .models import CustomUser

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['email', 'internal_id', 'full_name', 'nickname', 'grade']
        read_only_fields = ['email', 'internal_id']
