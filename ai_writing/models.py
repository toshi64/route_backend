from django.db import models
from instant_feedback.models import Session
from accounts.models import CustomUser
from material_scheduler.models import ScheduleComponent


class GrammarSubgenre(models.Model):
    """
    文法項目マスタテーブル
    既存のai_writing_grammarquestion.subgenreとの対応付け用
    """
    code = models.CharField(
        max_length=50,
        unique=True,
        help_text="文法項目コード (例: 'SV', 'Relative_Clause')"
    )
    name = models.CharField(
        max_length=100,
        help_text="表示用名称 (例: 'SV文型', '関係代名詞')"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="文法項目の詳細説明"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stra_grammar_subgenre'
        indexes = [
            models.Index(fields=['code']),  # name指定なし = Django自動生成
        ]
        ordering = ['code']

    def __str__(self):
        return f"{self.name} ({self.code})"

    @classmethod
    def create_from_existing_subgenres(cls):
        """
        既存のGrammarQuestionのsubgenre値からマスタデータを作成
        データ移行用のヘルパーメソッド
        """
        # 同じファイル内のGrammarQuestionを参照
        
        unique_subgenres = (GrammarQuestion.objects
                           .values_list('subgenre', flat=True)
                           .distinct())
        
        created_count = 0
        for code in unique_subgenres:
            if code:  # 空文字列を除外
                obj, created = cls.objects.get_or_create(
                    code=code,
                    defaults={
                        'name': code.replace('_', ' ').title(),
                        'description': f'自動生成: {code}'
                    }
                )
                if created:
                    created_count += 1
        
        return created_count
    

    

class GrammarQuestion(models.Model):
    id = models.AutoField(primary_key=True)
    custom_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    version = models.DecimalField(max_digits=3, decimal_places=1)
    created_by = models.CharField(max_length=100)
    question_text = models.TextField()
    genre = models.CharField(max_length=100)
    
    # 旧文字列フィールド（使用禁止・参照のみ）
    subgenre = models.CharField(
        max_length=100,
        editable=False,
        help_text="旧文字列列（使用禁止）"
    )
    
    # 新しいFK（NOT NULL・メイン使用）
    subgenre_fk = models.ForeignKey(
        GrammarSubgenre,
        on_delete=models.PROTECT,
        related_name='questions',
        help_text="文法項目への参照（メイン使用）"
    )
    
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
    subgenre_fk = models.ForeignKey(
        'GrammarSubgenre',
        on_delete=models.PROTECT,
        related_name='notes',
        db_column='subgenre_fk_id',   # 既存列名に合わせる
        null=True, blank=True,        # ← ここだけ一時的に True
        help_text='supabase 既存列を利用',
    )
    title = models.CharField(max_length=255)
    description = models.TextField(help_text="Markdownで記述された解説本文")

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"{self.subgenre}: {self.title}"


class AnswerUnit(models.Model):
    session = models.ForeignKey(
        Session,
        on_delete=models.SET_NULL,
        null=True,              # ★ここ
        blank=True,             # ★ここ
    )
    question = models.ForeignKey(GrammarQuestion, on_delete=models.SET_NULL, null=True, blank=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE) 
    user_answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    component = models.ForeignKey(ScheduleComponent, on_delete=models.SET_NULL, null=True, blank=True)
    is_review_target = models.BooleanField(default=False)
    
    # ✅ この行を追加
    stra_cycle_session = models.ForeignKey(
        'StraCycleSession',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='answer_units'
    )

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
    content = models.TextField()

    # 投稿日時
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Clip from {self.user} - {self.content[:20]} ({self.created_at})"


from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
import uuid

User = get_user_model()


class StraSession(models.Model):
    """
    Stra学習の教材レベルセッション（5周セット単位）
    Tadoku Sessionとの相同性を保持
    """
    
    class StatusChoices(models.TextChoices):
        ACTIVE = 'active', 'Active'
        COMPLETED = 'completed', 'Completed'
        REVIEW = 'review', 'Review'
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stra_sessions'
    )
    
    material = models.ForeignKey(
        'GrammarSubgenre',  # 同一app内のGrammarSubgenreを参照
        on_delete=models.CASCADE,
        related_name='stra_sessions'
    )
    
    # 一旦コメントアウト（スケジューラー機能は後で実装）
    # learning_context = models.ForeignKey(
    #     'scheduler.DailyAssignment',
    #     on_delete=models.SET_NULL,
    #     null=True,
    #     blank=True,
    #     related_name='stra_sessions'
    # )
    
    target_cycles = models.PositiveSmallIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="目標周回数（通常5回）"
    )
    
    completed_cycles = models.PositiveSmallIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="完了済み周回数"
    )
    
    status = models.CharField(
        max_length=10,
        choices=StatusChoices.choices,
        default=StatusChoices.ACTIVE
    )
    
    session_date = models.DateField(
        help_text="セッション開始日（03:00切り上げ基準）"
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="セッション開始時刻"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="セッション完了時刻"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stra_sessions'
        indexes = [
            # models.Index(fields=['learning_context']),  # 一旦コメントアウト
            models.Index(fields=['session_date']),
            models.Index(fields=['material']),
            models.Index(fields=['user']),
            models.Index(fields=['user', 'session_date']),
        ]
        constraints = [
            models.CheckConstraint(
                check=models.Q(completed_cycles__lte=models.F('target_cycles')),
                name='stra_sessions_cycles_logic_check'
            )
        ]
        verbose_name = 'Stra Session'
        verbose_name_plural = 'Stra Sessions'
    
    def __str__(self):
        return f"StraSession({self.user.username} - {self.material} - {self.completed_cycles}/{self.target_cycles})"
    
    @property
    def is_completed(self):
        """セッション完了判定"""
        return self.completed_cycles >= self.target_cycles
    
    @property
    def progress_percentage(self):
        """進捗率"""
        if self.target_cycles == 0:
            return 0
        return (self.completed_cycles / self.target_cycles) * 100
    
    def get_next_cycle_index(self):
        """次の周回番号を取得"""
        return self.completed_cycles + 1 if not self.is_completed else None


class StraCycleSession(models.Model):
    """
    Stra学習の周回レベルセッション（1周単位）
    旧instant_feedback_sessionとの互換性を保持
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    stra_session = models.ForeignKey(
        StraSession,
        on_delete=models.CASCADE,
        related_name='cycle_sessions'
    )
    
    cycle_index = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(20)],
        help_text="周回番号（1から開始）"
    )
    
    material = models.ForeignKey(
        'GrammarSubgenre',  # 高速JOIN用（冗長だが有益）
        on_delete=models.CASCADE,
        related_name='stra_cycle_sessions'
    )
    
    session_id = models.CharField(
        max_length=100,
        unique=True,
        help_text="旧互換用ユニークID（将来廃止予定）"
    )
    
    started_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="周回開始時刻（事前発行対応でNULL許容）"
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="周回完了時刻"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'stra_cycle_sessions'
        indexes = [
            models.Index(fields=['stra_session']),
            models.Index(fields=['material']),
            models.Index(fields=['session_id']),
            models.Index(fields=['stra_session', 'cycle_index']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['stra_session', 'cycle_index'],
                name='stra_cycle_sessions_unique_cycle'
            )
        ]
        verbose_name = 'Stra Cycle Session'
        verbose_name_plural = 'Stra Cycle Sessions'
    
    def __str__(self):
        return f"StraCycleSession({self.stra_session.user.username} - {self.material} - Cycle {self.cycle_index})"
    
    @property
    def is_completed(self):
        """周回完了判定"""
        return self.completed_at is not None
    
    @property
    def is_started(self):
        """周回開始判定"""
        return self.started_at is not None
    
    def save(self, *args, **kwargs):
        """保存時の自動処理"""
        # session_idの自動生成（未設定時）
        import uuid

        if not self.session_id:  # まだ値がない場合だけ
            self.session_id = uuid.uuid4().hex
                
                # material_idの自動設定（冗長フィールド）
        if not hasattr(self, 'material') or not self.material:
            self.material = self.stra_session.material
        
        super().save(*args, **kwargs)
        
        # 親セッションの進捗更新
        if self.is_completed:
            self._update_parent_progress()
    
    def _update_parent_progress(self):
        """親セッションの進捗を更新"""
        completed_count = self.stra_session.cycle_sessions.filter(
            completed_at__isnull=False
        ).count()
        
        self.stra_session.completed_cycles = completed_count
        
        # 全周回完了時はセッションも完了に
        if completed_count >= self.stra_session.target_cycles:
            self.stra_session.status = StraSession.StatusChoices.COMPLETED
            if not self.stra_session.completed_at:
                self.stra_session.completed_at = self.completed_at
        
        self.stra_session.save()


# データマイグレーション用のヘルパー関数
def migrate_old_sessions():
    """
    旧instant_feedback_sessionから新構造への移行
    """
    from .models import InstantFeedbackSession  # 旧モデル
    
    # 既存データのグループ化とStraSession作成
    # 実装は具体的な旧データ構造に依存
    pass


def update_sau_foreign_keys():
    """
    StudentAnswerUnitのFK更新
    """
    from .models import StudentAnswerUnit
    
    # FK差し替え処理
    # 実装は具体的なSAU構造に依存
    pass


from django.core.validators import MinLengthValidator
from django.db import models

class StraAnswerEvaluation(models.Model): 
    GRADE_CHOICES = [
        ('A', 'A - 優秀（ノーミス）'),
        ('B', 'B - 良好（軽微なミス）'), 
        ('C', 'C - 要改善（理解不足）'),
        ('D', 'D - 不十分（大幅な間違い）'),
    ]

    answer_unit = models.OneToOneField(
        AnswerUnit,
        on_delete=models.CASCADE,
        related_name='evaluation'
    )

    # ⭐ これだけで OK
    overall_grade = models.CharField(
        max_length=1,
        choices=GRADE_CHOICES,
        validators=[MinLengthValidator(1)]
    )

    # LLM 生データ（あとで詳細を取り出したくなった際に役立つ）
    raw_evaluation_json = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'stra_answerevaluation' 
        indexes = [models.Index(fields=['overall_grade'])]

    def __str__(self):
        return f"{self.answer_unit_id}: {self.overall_grade}"
