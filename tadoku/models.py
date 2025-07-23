from django.db import models


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