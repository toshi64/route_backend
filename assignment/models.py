# assignment/models.py
from django.db import models
from django.core.exceptions import ValidationError
# 1) 進捗ポインタ（そのままでOK）
class EnrollmentState(models.Model):
    enrollment = models.OneToOneField(
        "accounts.Enrollment", on_delete=models.CASCADE, related_name="state"
    )
    current_order_index = models.PositiveIntegerField(default=1)
    last_assigned_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.enrollment_id} → next #{self.current_order_index}"


# 2) 1日分の「行」（親）
class DailyAssignment(models.Model):
    class Status(models.TextChoices):
        NOT_DONE = "not_done", "Not done"       # 未完了（未着手／着手中も含む）
        COMPLETED = "completed", "Completed"    # 完了

    enrollment = models.ForeignKey(
        "accounts.Enrollment",
        on_delete=models.PROTECT,
        related_name="daily_assignments",
        db_index=True,
    )
    curriculum_id = models.CharField(max_length=64, db_index=True)
    order_index = models.PositiveIntegerField(db_index=True)
    target_date = models.DateField(db_index=True)

    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.NOT_DONE, db_index=True
    )
    # 任意：着手の有無を区別したいとき用（ダッシュボードで「取り組み中」表示に使える）
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("enrollment", "order_index")]  # 同順番は一度だけ
        indexes = [
            models.Index(fields=["enrollment", "target_date"]),
            models.Index(fields=["curriculum_id", "order_index"]),
        ]

    def __str__(self):
        return f"{self.enrollment_id} #{self.order_index} @ {self.target_date} [{self.status}]"


# 3) 行の中の各コンポーネント（子）
class DailyAssignmentItem(models.Model):
    class Component(models.TextChoices):
        STRA = "stra", "Stra"
        TADOKU = "tadoku", "Tadoku"

    class Status(models.TextChoices):
        NOT_DONE = "not_done", "Not done"
        COMPLETED = "completed", "Completed"

    assignment = models.ForeignKey(
        "assignment.DailyAssignment",
        on_delete=models.CASCADE,
        related_name="items",
        db_index=True,
    )
    component = models.CharField(max_length=16, choices=Component.choices)

    material_id = models.IntegerField(null=True, blank=True)

    stra_session = models.ForeignKey(
        "ai_writing.StraSession",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="assignment_items",
        db_index=True,
    )
    tadoku_session = models.ForeignKey(
        "tadoku.TadokuSession",
        null=True, blank=True, on_delete=models.SET_NULL,
        related_name="assignment_items",
        db_index=True,
    )

    status = models.CharField(
        max_length=12, choices=Status.choices, default=Status.NOT_DONE, db_index=True
    )
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    (models.Q(stra_session__isnull=True) & models.Q(tadoku_session__isnull=True))
                    | (models.Q(stra_session__isnull=False) & models.Q(tadoku_session__isnull=True))
                    | (models.Q(stra_session__isnull=True) & models.Q(tadoku_session__isnull=False))
                ),
                name="only_one_session_fk_filled",
            ),
            models.UniqueConstraint(fields=["assignment", "component"],
                                    name="uniq_assignment_component"),
        ]
        indexes = [models.Index(fields=["assignment", "status"])]

    def clean(self):
        filled = sum(v is not None for v in [self.stra_session_id, self.tadoku_session_id])
        if filled > 1:
            raise ValidationError("セッションFKは同時に1つまでです。")

    @property
    def session(self):
        return self.stra_session or self.tadoku_session

    def __str__(self):
        return f"{self.assignment_id}:{self.component} [{self.status}]"