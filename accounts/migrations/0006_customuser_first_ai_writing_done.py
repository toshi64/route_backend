# Generated by Django 5.2 on 2025-05-14 23:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0005_customuser_region_alter_customuser_first_name_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='first_ai_writing_done',
            field=models.BooleanField(default=False),
        ),
    ]
