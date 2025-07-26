from django.db import models
from django.db.models import Q, F 

class Material(models.Model):
    """Tadoku教材マスターテーブル"""
    title = models.CharField(max_length=255, verbose_name="教材タイトル")
    subgenre = models.CharField(max_length=100, verbose_name="サブジャンル")
    total_word_count = models.IntegerField(verbose_name="総語数")  # フロントエンド計算を避けるため
    total_sections = models.IntegerField(verbose_name="総セクション数")  # 進捗表示で使用
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        verbose_name = "教材"
        verbose_name_plural = "教材一覧"

    def __str__(self):
        return f"{self.title} ({self.subgenre})"


class MaterialSection(models.Model):
    """教材セクションテーブル"""
    material = models.ForeignKey(
        Material, 
        on_delete=models.CASCADE, 
        related_name='sections',
        verbose_name="教材"
    )
    section_number = models.IntegerField(verbose_name="セクション番号")
    text = models.TextField(verbose_name="英文")
    translation = models.TextField(verbose_name="日本語訳")
    word_count = models.IntegerField(verbose_name="語数")
    audio_url = models.URLField(max_length=500, verbose_name="音声URL", blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        verbose_name = "教材セクション"
        verbose_name_plural = "教材セクション一覧"
        ordering = ['section_number']
        unique_together = ['material', 'section_number']

    def __str__(self):
        return f"{self.material.title} - Section {self.section_number}"
    



from django.db import models
from django.contrib.auth import get_user_model
import uuid

User = get_user_model()

class TadokuSession(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tadoku_sessions')
    learning_context_id = models.CharField(max_length=36, null=True, blank=True, db_index=True)
    material = models.ForeignKey('Material', on_delete=models.PROTECT)
    target_cycles = models.PositiveIntegerField(default=5)
    completed_cycles = models.PositiveIntegerField(default=0)
    session_date = models.DateField(db_index=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tadoku_sessions'
        ordering = ['-session_date', '-created_at']
        indexes = [
            models.Index(fields=['user', 'session_date']),
            models.Index(fields=['learning_context_id']),
        ]
    
    def __str__(self):
        return f"TadokuSession({self.user.username}, {self.learning_context_id or 'No Context'}, {self.session_date})"
    
    @property
    def is_completed(self):
        return self.completed_cycles >= self.target_cycles
    
    @property
    def current_cycle(self):
        return self.completed_cycles + 1
    
    @property
    def progress_percentage(self):
        if self.target_cycles == 0:
            return 0
        return min(100, (self.completed_cycles / self.target_cycles) * 100)
    


class TadokuSessionStats(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(TadokuSession, on_delete=models.CASCADE, related_name='cycle_stats')
    cycle_number = models.PositiveIntegerField()
    sound_only_count = models.PositiveIntegerField(default=0)
    text_count = models.PositiveIntegerField(default=0)
    translation_count = models.PositiveIntegerField(default=0)
    total_pages = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tadoku_session_stats'
        unique_together = [('session', 'cycle_number')]
        constraints = [
            models.CheckConstraint(
                check=Q(total_pages=F('sound_only_count') + F('text_count') + F('translation_count')),
                name='check_total_equals_sum'
            )
        ]
        indexes = [
            models.Index(fields=['session']),
            models.Index(fields=['cycle_number']),
        ]
        
    def __str__(self):
        return f"Stats({self.session.id}, Cycle:{self.cycle_number}, S:{self.sound_only_count}/T:{self.text_count}/TR:{self.translation_count})"

    @property  
    def sound_ratio(self):
        return (self.sound_only_count / self.total_pages * 100) if self.total_pages > 0 else 0
        
    @property
    def text_ratio(self):
        return (self.text_count / self.total_pages * 100) if self.total_pages > 0 else 0
        
    @property
    def translation_ratio(self):
        return (self.translation_count / self.total_pages * 100) if self.total_pages > 0 else 0