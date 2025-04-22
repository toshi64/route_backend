import uuid
from django.db import migrations, models


def set_unique_internal_ids(apps, schema_editor):
    CustomUser = apps.get_model('accounts', 'CustomUser')
    for user in CustomUser.objects.all():
        user.internal_id = uuid.uuid4()
        user.save(update_fields=['internal_id'])


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        # Step 1: フィールドを追加（null=True 一時許容）
        migrations.AddField(
            model_name='customuser',
            name='internal_id',
            field=models.UUIDField(null=True, unique=True),
        ),

        # Step 2: 既存ユーザー2件に UUID を代入
        migrations.RunPython(set_unique_internal_ids),

        # Step 3: null=False に戻して完成
        migrations.AlterField(
            model_name='customuser',
            name='internal_id',
            field=models.UUIDField(unique=True),
        ),
    ]
