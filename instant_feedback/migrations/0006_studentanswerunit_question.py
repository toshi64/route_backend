# Generated by Django 5.2 on 2025-05-08 01:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('instant_feedback', '0005_eijakushindanquestion'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentanswerunit',
            name='question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='instant_feedback.eijakushindanquestion'),
        ),
    ]
